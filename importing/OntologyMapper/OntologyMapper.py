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


##############################################################################
# 1) GLOBAL HELPERS & CONSTANTS
##############################################################################

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

EMBEDDING_MODEL_MAP = {
    'matter': MatterEmbedding,
    'manufacturing': ProcessEmbedding,
    'measurement': ProcessEmbedding,
    'parameter': QuantityEmbedding,
    'property': QuantityEmbedding
}


##############################################################################
# 2) DATAPARSER
##############################################################################

class DataParser:
    """
    Class to parse CSV data and extract name/label information from the input data.
    This class does NOT do any ontology mapping; it only gathers the raw items
    that need to be mapped.
    """

    def __init__(self, data, file_link):
        """
        Initialize a DataParser instance.

        Args:
            data (dict): Graph data containing nodes and their attributes.
            file_link (str): Link to a CSV file containing additional info.
        """
        self.data = data
        self.file_link = file_link
        self._table = self._load_table()
        self._rows_to_map = []  # Will store (label, name_value) pairs

    def _load_table(self):
        """
        Load CSV data from a file node, decode, parse, and transpose.

        Returns:
            list[list[str]]: Transposed columns of CSV data.
        """
        file_node = File.nodes.get(link=self.file_link)
        file_content = file_node.get_file().decode('utf-8')
        csv_reader = csv.reader(StringIO(file_content))
        columns = list(zip(*csv_reader))
        # Remove empty values:
        return [list(filter(None, col)) for col in columns]

    def parse_data(self):
        """
        Go through each node in the data and extract (label, name_value) pairs.
        Skips 'metadata' label. If a node references a table index, collect
        all column values as well.
        """
        for node in self.data.get('nodes', []):
            if node.get('label') == 'metadata':
                continue

            label = node['label']
            names_field = node['attributes']['name']
            name_list = names_field if isinstance(names_field, list) else [names_field]

            for name_item in name_list:
                index_value = name_item.get('index', 'inferred')
                string_value = name_item.get('value')

                # If "inferred" or no table index is provided
                if index_value == 'inferred':
                    self._rows_to_map.append((label, string_value))
                else:
                    # Pull entire column from the CSV table
                    col_index = int(index_value)
                    for col_value in self._table[col_index]:
                        self._rows_to_map.append((label, col_value))

    @property
    def rows_to_map(self):
        """
        Returns:
            list[tuple(str, str)]: A list of (label, name_value) pairs
                                   extracted from the data.
        """
        return self._rows_to_map


##############################################################################
# 3) ONTOLOGY MAPPER
##############################################################################

class OntologyMapper:
    """
    Class responsible for taking a single name (plus context, label, and the
    corresponding ontology class) and mapping it to the ontology.
    """

    def __init__(self, context, label, ontology_class):
        """
        Args:
            context (str): Context to use when generating or connecting nodes.
            label (str): Category label for the name (e.g., 'matter', 'property').
            ontology_class (class): The corresponding Ontology class (e.g., EMMOMatter).
        """
        self.context = context
        self.label = label
        self.ontology_class = ontology_class

    def map_name(self, name_value):
        """
        Map a single name_value to the ontology, retrieving or creating a node.

        Args:
            name_value (str): The raw name to map.

        Returns:
            object: The ontology node that represents this name.
        """
        # Attempt to find similar nodes
        found_nodes = self.ontology_class.nodes.get_by_string(
            string=name_value.replace("_", " "),
            limit=15,
            include_similarity=True
        )
        # If no node is sufficiently similar, try to create a synonym or new node
        print(f"Found nodes for {name_value}: {found_nodes}")
        if not found_nodes or found_nodes[0][1] < 0.97:
            print("No Match Creating new node...")
            # Let's propose a synonym
            new_name = self._create_synonym(name_value, found_nodes)
            print(f"Proposed synonym: {new_name}")
            new_search = self.ontology_class.nodes.get_by_string(
                string=new_name, limit=15, include_similarity=True
            )
            print(f"New search results: {new_search}")
            if not new_search or new_search[0][1] < 0.97:
                print("still not found")
                # Create a brand new node
                ontology_node = self.ontology_class(name=new_name)
                self._save_node(ontology_node)
                return ontology_node
            else:
                return new_search[0][0]
        else:
            return found_nodes[0][0]

    def _save_node(self, node):
        """
        Save a newly created node, add embeddings, and connect it in the ontology.

        Args:
            node (object): An instance of the ontology node (e.g., EMMOMatter).
        """
        node.save()
        self._add_labels_create_embeddings(node)
        self._connect_to_ontology(node)

    def _create_synonym(self, input_text, found_nodes):
        """
        Use an LLM to propose a synonym for input_text if existing nodes are not sufficiently similar.

        Args:
            input_text (str): The text needing a synonym.
            found_nodes (list): Nodes returned by the ontology query (with similarity scores).

        Returns:
            str: A synonym or refined label from the LLM.
        """
        prompt = self._ontology_extension_prompt(input_text, found_nodes)
        # Use your existing chat_with_gpt3 function
        output = chat_with_gpt3(prompt=prompt, setup_message=SETUP_MESSAGES[self.label])
        return output

    def _ontology_extension_prompt(self, input_text, ontology_list):
        """
        Format a prompt describing the context and candidate ontology nodes for the LLM.

        Args:
            input_text (str): The raw text to be extended/refined.
            ontology_list (list): List of found ontology nodes with similarities.

        Returns:
            str: Formatted prompt text.
        """
        candidate_names = ", ".join([n[0].name for n in ontology_list])
        return (
            f"Input: {input_text}\n"
            f"Context: {self.context}\n"
            f"Candidates: {candidate_names}"
        )

    def _add_labels_create_embeddings(self, node):
        """
        Add alternative labels and embeddings to a node after it is created.

        Args:
            node (object): The newly created node.
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
        label_info = ontology_manager.get_labels(
            node.name,
            SETUP_MAPPER_MESSAGES[self.label],
            examples=SETUP_MAPPER_EXAMPLES[self.label]
        )

        # Attach each alternative label
        for alt_label in label_info.alternative_labels:
            embedding_vec = request_embedding(alt_label)
            embedding_node = EMBEDDING_MODEL_MAP[self.label](
                vector=embedding_vec,
                input=alt_label
            ).save()
            node.model_embedding.connect(embedding_node)

        # Also embed the main name
        main_embedding = request_embedding(node.name)
        main_embedding_node = EMBEDDING_MODEL_MAP[self.label](
            vector=main_embedding,
            input=node.name
        ).save()
        node.model_embedding.connect(main_embedding_node)

    def _connect_to_ontology(self, node):
        """
        Attempts to connect a node in the ontology by finding super-/subclass candidates.

        Args:
            node (object): The newly created or retrieved node.
        """
        if not node.emmo_subclass and not node.emmo_parentclass:
            print("Connecting node to ontology...")
            candidates = self._find_candidates(node)
            print(f"Candidates for {node.name}: {candidates}")
            connection_names = self._find_connection(node.name, candidates)
            print(f"Connection chain: {connection_names}")
            previous_node = None
            for cname in connection_names:
                # Check if there is an existing node with that name
                search_res = node.nodes.get_by_string(
                    string=cname,
                    limit=8,
                    include_similarity=True
                )
                if search_res and search_res[0][1] > 0.98:
                    current_node = search_res[0][0]
                else:
                    current_node = self.ontology_class(name=cname)
                    current_node.save()

                if previous_node and previous_node != current_node:
                    print(f"Connecting: {previous_node.name} -> {current_node.name}")
                    previous_node.emmo_parentclass.connect(current_node)
                previous_node = current_node
        else:
            print(f"Node already connected: {node.name} -> {node.emmo_parentclass}, {node.emmo_subclass}")

    def _find_candidates(self, node):
        """
        Use an LLM to suggest parent or child candidates for the node in the ontology.

        Args:
            node (object): The node needing candidates.

        Returns:
            list: A list of candidate nodes or classes for linking.
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

        llm = ChatOpenAI(model_name=CHAT_GPT_MODEL, openai_api_key=os.getenv("OPENAI_API_KEY"))
        setup_message = ONTOLOGY_CANDIDATES[self.ontology_class._meta.object_name]
        prompt = ChatPromptTemplate.from_messages(setup_message)

        # Potential matches:
        raw_candidates = self.ontology_class.nodes.get_by_string(
            string=node.name, limit=8, include_similarity=False
        )
        candidate_names = ", ".join([c.name for c in raw_candidates if c.name != node.name])
        query = f"Input: {node.name}\nCandidates: {candidate_names}\nContext: {self.context}"

        # Add few-shot examples if available
        if examples := ONTOLOGY_CANDIDATES_EXAMPLES[self.ontology_class._meta.object_name]:
            example_prompt = ChatPromptTemplate.from_messages([('human', "{input}"), ('ai', "{output}")])
            few_shot_prompt = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=examples)
            prompt = ChatPromptTemplate.from_messages([setup_message[0], few_shot_prompt, *setup_message[1:]])

        chain = create_structured_output_runnable(Response, llm, prompt).with_config(
            {"run_name": f"{node.name}-generation"}
        )
        ontology_advice = chain.invoke({"input": query})

        chosen_candidate = ontology_advice.answer
        if chosen_candidate is None:
            # No suggestion from LLM, gather superclasses for all potential matches
            uids = list(dict.fromkeys([c.uid for c in raw_candidates if c.name != node.name]))
            return node.get_superclasses(uids)
        elif isinstance(chosen_candidate, ChildClass):
            # LLM suggests a child
            target_uid = raw_candidates[[c.name for c in raw_candidates].index(chosen_candidate.child_name)].uid
            return node.get_subclasses([target_uid])
        else:
            # LLM suggests a parent
            target_uid = raw_candidates[[c.name for c in raw_candidates].index(chosen_candidate.parent_name)].uid
            return node.get_superclasses([target_uid])

    @retry(stop=stop_after_attempt(4), wait=wait_fixed(2))
    def _find_connection(self, name, candidates):
        """
        Given a list of candidate classes, use an LLM to find the connection chain.

        Args:
            candidates (list): Candidate classes or nodes.

        Returns:
            list[str]: Class names in the order they should be connected.
        """
        ONTOLOGY_CONNECTOR = {
            'EMMOMatter': MATTER_ONTOLOGY_CONNECTOR_MESSAGES,
            'EMMOProcess': PROCESS_ONTOLOGY_CONNECTOR_MESSAGES,
            'EMMOQuantity': QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES,
        }

        llm = ChatOpenAI(model_name=CHAT_GPT_MODEL, openai_api_key=os.getenv("OPENAI_API_KEY"))
        setup_message = ONTOLOGY_CONNECTOR[self.ontology_class._meta.object_name]
        names_for_prompt = ", ".join([c[1] for c in candidates])
        query = f"Input: {name}, candidates: {names_for_prompt}"

        prompt = ChatPromptTemplate.from_messages(setup_message)
        chain = create_structured_output_runnable(ClassList, llm, prompt).with_config(
            {"run_name": f"{name}-connection"}
        )
        response = chain.invoke({"input": query})
        return [cls.name for cls in response.classes]


##############################################################################
# 4) PIPELINE CLASS
##############################################################################

class OntologyPipeline:
    """
    Single-step pipeline class that:
      1. Parses the provided data & CSV using DataParser.
      2. Maps each name to the ontology using OntologyMapper.
      3. Collects and returns the results.
    """

    def __init__(self, data, file_link, context):
        """
        Args:
            data (dict): Input data (including nodes, attributes).
            file_link (str): Link to the CSV file containing columns.
            context (str): Context string used during ontology mapping.
        """
        self.data = data
        self.file_link = file_link
        self.context = context
        self._results = []  # Will hold {'name': str, 'label': str, 'uid': ...}

    def run(self):
        """
        Run the pipeline: parse data and map each (label, name_value) to an ontology node.
        """
        # 1) Parse the data
        parser = DataParser(self.data, self.file_link)
        parser.parse_data()

        # 2) For each (label, name_value) pair, map to ontology
        seen_pairs = set()  # Avoid re-mapping duplicates
        for label, name_value in parser.rows_to_map:
            if (label, name_value) in seen_pairs:
                continue

            seen_pairs.add((label, name_value))
            # Skip metadata, just in case
            if label == 'metadata':
                continue

            if label in ONTOLOGY_CLASS_MAP:
                ontology_class = ONTOLOGY_CLASS_MAP[label]
                mapper = OntologyMapper(self.context, label, ontology_class)
                node = mapper.map_name(name_value)
                # Store result
                self._results.append({
                    'name': name_value,
                    'label': label,
                    'uid': node.uid,
                    'ontology_class': ontology_class.__name__
                })
            else:
                print(f"Unknown label: {label}. Skipping...")

    @property
    def results(self):
        """
        Returns:
            list[dict]: A list of mappings with fields:
                          - name (str)
                          - label (str)
                          - uid (str)
                          - ontology_class (str)
        """
        return self._results



