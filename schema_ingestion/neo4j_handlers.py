import csv
import csv
import os
from io import StringIO

from langchain_community.chains.ernie_functions.base import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_fixed

from graphutils.config import CHAT_GPT_MODEL
from graphutils.embeddings import request_embedding
# from graphutils.models import AlternativeLabel
from importing.OntologyMapper.setupMessages import (
    PARAMETER_SETUP_MESSAGE,
    MEASUREMENT_SETUP_MESSAGE,
    MANUFACTURING_SETUP_MESSAGE,
    MATTER_SETUP_MESSAGE,
    PROPERTY_SETUP_MESSAGE
)
from importing.utils.openai import chat_with_gpt3
from matgraph.models.embeddings import MatterEmbedding, ProcessEmbedding, QuantityEmbedding
from matgraph.models.metadata import File
from matgraph.models.ontology import EMMOMatter, EMMOProcess, EMMOQuantity
from ontologymanagement.examples import (
    MATTER_ONTOLOGY_CANDIDATES_EXAMPLES,
    PROCESS_ONTOLOGY_CANDIDATES_EXAMPLES,
    QUANTITY_ONTOLOGY_CANDIDATES_EXAMPLES,
    MATTER_ONTOLOGY_ASSISTANT_EXAMPLES,
    PROCESS_ONTOLOGY_ASSISTANT_EXAMPLES,
    QUANTITY_ONTOLOGY_ASSISTANT_EXAMPLES
)
from ontologymanagement.ontologyManager import OntologyManager
from ontologymanagement.schema import Response, ChildClass, ClassList
from ontologymanagement.setupMessages import (
    MATTER_ONTOLOGY_CANDIDATES_MESSAGES,
    PROCESS_ONTOLOGY_CANDIDATES_MESSAGES,
    QUANTITY_ONTOLOGY_CANDIDATES_MESSAGES,
    MATTER_ONTOLOGY_CONNECTOR_MESSAGES,
    PROCESS_ONTOLOGY_CONNECTOR_MESSAGES,
    QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES,
    MATTER_ONTOLOGY_ASSISTANT_MESSAGES,
    PROCESS_ONTOLOGY_ASSISTANT_MESSAGES,
    QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES
)

# Renamed from ONTOLOGY_MAPPER to avoid confusion with the new OntologyMapper class
ONTOLOGY_CLASS_MAP = {
    'matter': EMMOMatter,
    'manufacturing': EMMOProcess,
    'measurement': EMMOProcess,
    'parameter': EMMOQuantity,
    'property': EMMOQuantity
}

SETUP_MESSAGES = {
    'matter': MATTER_SETUP_MESSAGE,
    'manufacturing': MANUFACTURING_SETUP_MESSAGE,
    'measurement': MEASUREMENT_SETUP_MESSAGE,
    'parameter': PARAMETER_SETUP_MESSAGE,
    'property': PROPERTY_SETUP_MESSAGE
}

EMBEDDING_MODEL_MAPPER = {
    'matter': MatterEmbedding,
    'manufacturing': ProcessEmbedding,
    'measurement': ProcessEmbedding,
    'parameter': QuantityEmbedding,
    'property': QuantityEmbedding
}


class DataParser:
    """
    Class to parse CSV data and iterate over nodes in the provided data.
    Calls OntologyMapper to handle the actual ontology mapping for each name.
    """

    def __init__(self, data, file_link, context):
        """
        Initialize a DataParser instance.

        Args:
            data (dict): Data containing nodes and their attributes to be parsed.
            file_link (str): Link to a file containing table data in CSV format.
            context (str): Contextual information used during ontology mapping.
        """
        self.data = data
        self.file_link = file_link
        self.context = context
        self._mapping = []
        self.names = []
        self._table = self._load_table(file_link)

    def _load_table(self, file_link):
        """
        Load CSV data from a file and transpose rows to columns.

        Args:
            file_link (str): Link to the CSV file.

        Returns:
            list: A list of columns with non-empty values from the CSV.
        """
        file = File.nodes.get(link=file_link)
        file_content = file.get_file().decode('utf-8')
        csv_reader = csv.reader(StringIO(file_content))
        columns = list(zip(*csv_reader))  # Transpose rows to columns
        return [list(filter(None, col)) for col in columns]  # Remove empty values

    def parse_data(self):
        """
        Parse the provided data, skipping nodes labeled 'metadata',
        and mapping each name using the OntologyMapper class.
        """
        for node in self.data['nodes']:
            if node['label'] == 'metadata':
                continue
            # Ensure 'name' attribute is a list
            node['name'] = (
                [node['attributes']['name']]
                if not isinstance(node['attributes']['name'], list)
                else node['attributes']['name']
            )
            for node_name in node['name']:
                self._process_node(node, node_name)

    def _process_node(self, node, name):
        """
        Process an individual node, either appending mapping directly
        or handling table-based mapping.

        Args:
            node (dict): The node data to be processed.
            name (dict or str): The name or structured name of the node.
        """
        label = node['label']

        index_value = name.get('index', 'inferred')
        value_value = name.get('value')

        if index_value == 'inferred' or value_value not in self.names:
            self._append_mapping(value_value, label)
        elif label != 'metadata':
            self._handle_table_mapping(name, label)

    def _handle_table_mapping(self, name, label):
        """
        Handle mapping for nodes referencing table data.

        Args:
            name (dict): A dictionary containing index and value information.
            label (str): The label of the node.
        """
        for col_value in self._table[int(name['index'])]:
            if col_value not in self.names:
                self._append_mapping(col_value, label)

    def _append_mapping(self, name_value, label):
        """
        Append a new mapping for a node and generate an ontology node if necessary.

        Args:
            name_value (str): The value of the node's name.
            label (str): The label/category of the node.
        """
        print(name_value, label)
        if label == 'metadata':
            return
        mapper = OntologyMapper(self.context, name_value, label, ONTOLOGY_CLASS_MAP[label])
        if name_value not in [mapping['name'] for mapping in self._mapping]:
            node_uid = mapper.map_name_to_ontology(name_value, label).uid
            self._mapping.append({
                'name': name_value,
                'id': node_uid,
                'ontology_label': ONTOLOGY_CLASS_MAP[label].__name__,
                'label': label.upper()
            })
            self.names.append(name_value)

    @property
    def mapping(self):
        """
        Property to access the current mapping list.

        Returns:
            list: A list of mappings that have been created.
        """
        return self._mapping

    def run(self):
        """
        Execute the data parsing and ontology mapping process for all nodes.
        """
        self.parse_data()


class OntologyMapper:
    """
    Class responsible for taking a single name (plus context and label)
    and mapping it to an ontology node. If the node does not exist, it is created;
    otherwise, the existing node is retrieved. Also handles connecting nodes,
    finding candidates, and adding labels/embeddings.
    """

    def __init__(self, context, name, label, ontology_class):
        """
        Initialize an OntologyMapper instance.

        Args:
            context (str): Contextual information for ontology generation.
            name (str): The name of the entity to be generated or retrieved.
            label (str): The category label (e.g., 'matter', 'parameter').
            ontology_class (class): The ontology class corresponding to the label.
        """
        self.context = context
        self.name = name
        self.label = label
        self.ontology_class = ontology_class

    def map_name_to_ontology(self, input_name, label):
        """
        Main entry point for mapping a single name to the ontology.
        Retrieves or creates an ontology node, then returns that node.

        Args:
            input_name (str): The input string to map onto the ontology.
            label (str): The label/category for this ontology node.

        Returns:
            object: The ontology node that matches the given name.
        """
        existing_nodes = self.ontology_class.nodes.get_by_string(
            string=input_name.replace("_", " "), limit=15, include_similarity=True
        )
        # If there's no sufficiently similar node, create a new synonym or node
        if existing_nodes[0][1] < 0.97:
            output = self.create_synonym(input_name, existing_nodes, label)
            new_search = self.ontology_class.nodes.get_by_string(
                string=output, limit=15, include_similarity=True
            )
            if new_search[0][1] < 0.97:
                ontology_node = self.ontology_class(name=output)
                self.save_ontology_node(ontology_node)
                return ontology_node
            else:
                return new_search[0][0]
        else:
            # Return the best match
            return existing_nodes[0][0]

    def save_ontology_node(self, node):
        """
        Save an ontology node, then add labels/embeddings and attempt to connect it in the ontology.

        Args:
            node (object): The ontology node to save.
        """
        node.save()  # Assuming node has a save method for basic saving operations
        self.add_labels_create_embeddings(node)
        self.connect_to_ontology(node)

    def connect_to_ontology(self, node):
        """
        Connect a node to the ontology by finding candidate superclasses or subclasses
        and linking them in a chain if the node is not already connected.

        Args:
            node (object): The ontology node to connect in the ontology.
        """
        if not node.emmo_subclass and not node.emmo_parentclass:
            candidates = self.find_candidates(node)
            connection_names = self.find_connection(candidates)
            previous_node = None
            for name in connection_names:
                # Search for a similar node by name
                search_results = node.nodes.get_by_string(
                    string=name, limit=8, include_similarity=True
                )
                if search_results and search_results[0][1] > 0.98:
                    current_node = search_results[0][0]
                else:
                    current_node = self.ontology_class(name=name)
                    current_node.save()
                # Connect the chain
                if previous_node and previous_node != current_node:
                    previous_node.emmo_parentclass.connect(current_node)

                previous_node = current_node
        else:
            print(f"Connected node? {node.name} {node.emmo_subclass}, {node.emmo_parentclass} ")

    def find_candidates(self, node):
        """
        Find candidate ontology nodes that may be related to the given node
        based on an LLM's advice (using few-shot and structured output).

        Args:
            node (object): The node to find candidates for.

        Returns:
            list: A list of candidate ontology nodes or related classes based on LLM advice.
        """
        ONTOLOGY_CANDIDATES = {
            'EMMOMatter': MATTER_ONTOLOGY_CANDIDATES_MESSAGES,
            'EMMOProcess': PROCESS_ONTOLOGY_CANDIDATES_MESSAGES,
            'EMMOQuantity': QUANTITY_ONTOLOGY_CANDIDATES_MESSAGES
        }

        ONTOLOGY_CANDIDATES_EXAMPLES = {
            'EMMOMatter': MATTER_ONTOLOGY_CANDIDATES_EXAMPLES,
            'EMMOProcess': PROCESS_ONTOLOGY_CANDIDATES_EXAMPLES,
            'EMMOQuantity': QUANTITY_ONTOLOGY_CANDIDATES_EXAMPLES
        }
        nodes = self.ontology_class.nodes.get_by_string(
            string=node.name, limit=8, include_similarity=False
        )
        llm = ChatOpenAI(model_name=CHAT_GPT_MODEL, openai_api_key=os.getenv("OPENAI_API_KEY"))

        setup_message = ONTOLOGY_CANDIDATES[self.ontology_class._meta.object_name]
        prompt = ChatPromptTemplate.from_messages(setup_message)

        query = (
            f"Input: {node.name}\n"
            f"Candidates: {', '.join([el.name for el in nodes if el.name != node.name])} \n"
            f"Context: {self.context}"
        )

        if examples := ONTOLOGY_CANDIDATES_EXAMPLES[self.ontology_class._meta.object_name]:
            example_prompt = ChatPromptTemplate.from_messages([('human', "{input}"), ('ai', "{output}")])
            few_shot_prompt = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=examples)
            prompt = ChatPromptTemplate.from_messages([setup_message[0], few_shot_prompt, *setup_message[1:]])

        chain = create_structured_output_runnable(Response, llm, prompt).with_config(
            {"run_name": f"{node.name}-generation"}
        )
        ontology_advice = chain.invoke({"input": query})

        # If no specific candidate is suggested, or an incomplete answer is given
        if (chosen_candidate := ontology_advice.answer) is None:
            uids = list(dict.fromkeys([node.uid for node in nodes if node.name != self.name]))
            return node.get_superclasses(uids)
        elif isinstance(ontology_advice.answer, ChildClass):
            candidate_uid = nodes[[node.name for node in nodes].index(chosen_candidate.child_name)].uid
            return node.get_subclasses([candidate_uid])
        else:
            candidate_uid = nodes[[node.name for node in nodes].index(chosen_candidate.parent_name)].uid
            return node.get_superclasses([candidate_uid])

    @retry(stop=stop_after_attempt(4), wait=wait_fixed(2))
    def find_connection(self, candidates):
        """
        Use an LLM-based approach to determine how to connect the given candidates,
        returning a list of class names forming a connection chain.

        Args:
            candidates (list): List of candidate ontology nodes.

        Returns:
            list: A list of class names to connect in a hierarchical chain.
        """
        ONTOLOGY_CONNECTOR = {
            'EMMOMatter': MATTER_ONTOLOGY_CONNECTOR_MESSAGES,
            'EMMOProcess': PROCESS_ONTOLOGY_CONNECTOR_MESSAGES,
            'EMMOQuantity': QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES,
        }

        llm = ChatOpenAI(model_name=CHAT_GPT_MODEL, openai_api_key=os.getenv("OPENAI_API_KEY"))
        setup_message = ONTOLOGY_CONNECTOR[self.ontology_class._meta.object_name]
        query = f"Input: {self.name}, candidates: {', '.join([el[1] for el in candidates])}"
        prompt = ChatPromptTemplate.from_messages(setup_message)

        chain = create_structured_output_runnable(ClassList, llm, prompt).with_config(
            {"run_name": f"{self.name}-connection"}
        )
        response = chain.invoke({"input": query})
        return [el.name for el in response.classes]

    def add_labels_create_embeddings(self, node):
        """
        Enrich the node by adding alternative labels and embeddings for each label,
        connecting them to the node.

        Args:
            node (object): The node to enrich with labels and embeddings.
        """
        SETUP_MAPPER_EXAMPLES = {
            'matter': MATTER_ONTOLOGY_ASSISTANT_EXAMPLES,
            'manufacturing': PROCESS_ONTOLOGY_ASSISTANT_EXAMPLES,
            'measurement': PROCESS_ONTOLOGY_ASSISTANT_EXAMPLES,
            'property': QUANTITY_ONTOLOGY_ASSISTANT_EXAMPLES,
            'parameter': QUANTITY_ONTOLOGY_ASSISTANT_EXAMPLES
        }
        SETUP_MAPPER_MESSAGES = {
            'matter': MATTER_ONTOLOGY_ASSISTANT_MESSAGES,
            'manufacturing': PROCESS_ONTOLOGY_ASSISTANT_MESSAGES,
            'measurement': PROCESS_ONTOLOGY_ASSISTANT_MESSAGES,
            'property': QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES,
            'parameter': QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES
        }
        ontology_manager = OntologyManager()
        ontology_class = ontology_manager.get_labels(
            node.name,
            SETUP_MAPPER_MESSAGES[self.label],
            examples=SETUP_MAPPER_EXAMPLES[self.label]
        )
        for alt_label in ontology_class.alternative_labels:
            # alternative_label_node = AlternativeLabel(label=alt_label).save()
            # node.alternative_label.connect(alternative_label_node)
            embedding = request_embedding(alt_label)
            embedding_node = EMBEDDING_MODEL_MAPPER[self.label](
                vector=embedding,
                input=alt_label
            ).save()
            node.model_embedding.connect(embedding_node)

        # Create embedding for the node's main name
        embedding_node = EMBEDDING_MODEL_MAPPER[self.label](
            vector=request_embedding(node.name),
            input=node.name
        ).save()
        node.model_embedding.connect(embedding_node)

    def ontology_extension_prompt(self, input_text, ontology_list):
        """
        Create a prompt string for extending the ontology based on an input text
        and current ontology candidates.

        Args:
            input_text (str): The input text (node name).
            ontology_list (list): List of ontology candidates.

        Returns:
            str: A formatted prompt string incorporating context and candidates.
        """
        return (
            f"Input: {input_text}\n"
            f"Context: {self.context}\n"
            f"Candidates: {', '.join([ont[0].name for ont in ontology_list])}"
        )

    def create_synonym(self, input_text, ontology_list, label):
        """
        Use an LLM to create a synonym for an input text that doesn't match
        existing ontology nodes closely.

        Args:
            input_text (str): The text for which to create a synonym.
            ontology_list (list): List of candidate ontology nodes.
            label (str): The label/category of the input text.

        Returns:
            str: A synonym or adjusted string from the LLM.
        """
        prompt = self.ontology_extension_prompt(input_text, ontology_list)
        output = chat_with_gpt3(prompt=prompt, setup_message=SETUP_MESSAGES[label])
        return output

    def extend_ontology(self, input_text, ontology_list, label):
        """
        Create and save a new ontology node, effectively extending the ontology.

        Args:
            input_text (str): The name for the new ontology node.
            ontology_list (list): Related ontology candidates (unused here).
            label (str): The label/category of the new node.

        Returns:
            object: The newly created ontology node.
        """
        ontology_node = self.ontology_class(name=input_text)
        self.save_ontology_node(ontology_node)
        return ontology_node
