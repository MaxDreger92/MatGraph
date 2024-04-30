import csv
import csv
import os
from io import StringIO

from langchain.chains.ernie_functions import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI

from graphutils.embeddings import request_embedding
from graphutils.models import AlternativeLabel
from importing.OntologyMapper.setupMessages import PARAMETER_SETUP_MESSAGE, MEASUREMENT_SETUP_MESSAGE, \
    MANUFACTURING_SETUP_MESSAGE, MATTER_SETUP_MESSAGE, PROPERTY_SETUP_MESSAGE
from importing.utils.openai import chat_with_gpt3
from matgraph.models.embeddings import MatterEmbedding, ProcessEmbedding, QuantityEmbedding
from matgraph.models.metadata import File
from matgraph.models.ontology import EMMOMatter, EMMOProcess, EMMOQuantity
from ontologymanagement.examples import MATTER_ONTOLOGY_CANDIDATES_EXAMPLES, PROCESS_ONTOLOGY_CANDIDATES_EXAMPLES, \
    QUANTITY_ONTOLOGY_CANDIDATES_EXAMPLES, MATTER_ONTOLOGY_ASSISTANT_EXAMPLES, PROCESS_ONTOLOGY_ASSISTANT_EXAMPLES, \
    QUANTITY_ONTOLOGY_ASSISTANT_EXAMPLES
from ontologymanagement.ontologyManager import OntologyManager
from ontologymanagement.schema import Response, ChildClass, ClassList
from ontologymanagement.setupMessages import MATTER_ONTOLOGY_CANDIDATES_MESSAGES, PROCESS_ONTOLOGY_CANDIDATES_MESSAGES, \
    QUANTITY_ONTOLOGY_CANDIDATES_MESSAGES, MATTER_ONTOLOGY_CONNECTOR_MESSAGES, PROCESS_ONTOLOGY_CONNECTOR_MESSAGES, \
    QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES, MATTER_ONTOLOGY_ASSISTANT_MESSAGES, PROCESS_ONTOLOGY_ASSISTANT_MESSAGES, \
    QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES

ONTOLOGY_MAPPER = {
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


class OntologyMapper:

    def __init__(self, data, file_link, context):
        self.data = data
        self.file_link = file_link
        self.context = context
        self._mapping = []
        self.names = []
        self._table = self._load_table(file_link)

    def _load_table(self, file_link):
        file = File.nodes.get(link=file_link)
        file_content = file.get_file().decode('utf-8')
        csv_reader = csv.reader(StringIO(file_content))
        columns = list(zip(*csv_reader))  # Transpose rows to columns
        return [list(filter(None, col)) for col in columns]  # Remove empty values

    def map_on_ontology(self):
        for node in self.data['nodes']:
            node['name'] = [node['name']] if not isinstance(node['name'], list) else node['name']
            for node_name in node['name']:
                self._process_node(node, node_name)

    def _process_node(self, node, name):
        label = node['label']
        if name['index'] == 'inferred' or name['value'] not in self.names:
            self._append_mapping(name['value'], label)
        elif label != 'metadata':
            self._handle_table_mapping(name, label)

    def _handle_table_mapping(self, name, label):
        for col_value in self.table[int(name['index'])]:
            if col_value not in self.names:
                self._append_mapping(col_value, label)

    def _append_mapping(self, name_value, label):
        if label == 'metadata':
            return
        ontology_generator = OntologyGenerator(self.context, name_value, label, ONTOLOGY_MAPPER[label])
        if name_value not in [mapping['name'] for mapping in self._mapping]:
            node_uid = ontology_generator.get_or_create(name_value, label).uid
            self._mapping.append({'name': name_value,
                                  'id': node_uid,
                                  'ontology_label': ONTOLOGY_MAPPER[label].__name__,
                                  'label': label.upper()})
            self.names.append(name_value)

    @property
    def table(self):
        return self._table

    @property
    def mapping(self):
        return self._mapping

    def run(self):
        self.map_on_ontology()


class OntologyGenerator:

    def __init__(self, context, name, label, ontology_class):
        self.context = context
        self.name = name
        self.label = label
        self.ontology_class = ontology_class

    def get_or_create(self, input, label):
        ontology = ONTOLOGY_MAPPER[label].nodes.get_by_string(string=input.replace("_", " "), limit=15,
                                                              include_similarity=True)
        return ontology[0][0]
        # if ontology[0][1] < 0.97:
        #     output = self.create_synonym(input, ontology, label)
        #     nodes = ONTOLOGY_MAPPER[label].nodes.get_by_string(string=output, limit=15, include_similarity=True)
        #     if nodes[0][1] < 0.97:
        #         ontology_node = ONTOLOGY_MAPPER[label](name=output)
        #         self.save_ontology_node(ontology_node)
        #         return ontology_node
        #     else:
        #         return nodes[0][0]
        # else:
        #     return ontology[0][0]

    def save_ontology_node(self, node):
        """
        Save an ontology node with the option to add labels, create embeddings, and connect to the ontology.

        :param node: The ontology node to save.
        :param add_labels_create_embeddings: Flag to add labels and create embeddings.
        :param connect_to_ontology: Flag to connect the node to the ontology.
        """
        node.save()  # Assuming node has a save method for basic saving operations
        self.add_labels_create_embeddings(node)
        self.connect_to_ontology(node)

    def connect_to_ontology(self, node):
        # Check if the node is already connected in the ontology
        if not node.emmo_subclass and not node.emmo_parentclass:
            candidates = self.find_candidates(node)
            connection_names = self.find_connection(candidates)
            previous_node = None
            for name in connection_names:
                # Search for the node by name, with similarity consideration
                search_results = node.nodes.get_by_string(string=name, limit=8, include_similarity=True)
                if search_results and search_results[0][1] > 0.98:
                    # A similar node is found
                    current_node = search_results[0][0]
                else:
                    # No similar node found, or similarity is too low; create a new node
                    current_node = self.ontology_class(name=name)
                    current_node.save()
                # Connect the current node to the previous one in the chain, if applicable
                if previous_node and previous_node != current_node:
                    previous_node.emmo_parentclass.connect(current_node)

                previous_node = current_node
        else:
            print(f"Connected node? {node.name} {node.emmo_sublcass}, {node.emmo_parentclass} ")

    def find_candidates(self, node):
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
        nodes = self.ontology_class.nodes.get_by_string(string=node.name, limit=8, include_similarity=False)
        llm = ChatOpenAI(model_name="gpt-4-1106-preview", openai_api_key=os.getenv("OPENAI_API_KEY"))
        setup_message = ONTOLOGY_CANDIDATES[self.ontology_class._meta.object_name]
        prompt = ChatPromptTemplate.from_messages(setup_message)
        query = f"""Input: {node.name}\nCandidates: {", ".join([el.name for el in nodes if el.name != node.name])} \nContext: {self.context}"""
        if examples := ONTOLOGY_CANDIDATES_EXAMPLES[self.ontology_class._meta.object_name]:
            example_prompt = ChatPromptTemplate.from_messages([('human', "{input}"), ('ai', "{output}")])
            few_shot_prompt = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=examples)
            prompt = ChatPromptTemplate.from_messages([setup_message[0], few_shot_prompt, *setup_message[1:]])

        chain = create_structured_output_runnable(Response, llm, prompt).with_config(
            {"run_name": f"{node.name}-generation"})
        ontology_advice = chain.invoke({"input": query})
        if (chosen_candidate := ontology_advice.answer) is None:
            uids = list(dict.fromkeys([node.uid for node in nodes if node.name != self.name]))
            return node.get_superclasses(uids)
        elif isinstance(ontology_advice.answer, ChildClass):
            candidate_uid = nodes[[node.name for node in nodes].index(chosen_candidate.child_name)].uid
            return node.get_subclasses([candidate_uid])
        else:
            candidate_uid = nodes[[node.name for node in nodes].index(chosen_candidate.parent_name)].uid
            return node.get_superclasses([candidate_uid])

    def find_connection(self, candidates):
        ONTOLOGY_CONNECTOR = {
            'EMMOMatter': MATTER_ONTOLOGY_CONNECTOR_MESSAGES,
            'EMMOProcess': PROCESS_ONTOLOGY_CONNECTOR_MESSAGES,
            'EMMOProcess': PROCESS_ONTOLOGY_CONNECTOR_MESSAGES,
            'EMMOQuantity': QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES,
            'EMMOQuantity': QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES
        }

        llm = ChatOpenAI(model_name="gpt-4-1106-preview", openai_api_key=os.getenv("OPENAI_API_KEY"))
        setup_message = ONTOLOGY_CONNECTOR[self.ontology_class._meta.object_name]
        query = f"""Input: {self.name}, candidates: {', '.join([el[1] for el in candidates])}"""
        prompt = ChatPromptTemplate.from_messages(setup_message)
        chain = create_structured_output_runnable(ClassList, llm, prompt).with_config(
            {"run_name": f"{self.name}-connection"})
        response = chain.invoke({"input": query})
        return [el.name for el in response.classes]

    def add_labels_create_embeddings(self, node):
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
        ontology_class = ontology_manager.get_labels(node.name, SETUP_MAPPER_MESSAGES[self.label],
                                                     examples=SETUP_MAPPER_EXAMPLES[self.label])
        for label in ontology_class.alternative_labels:
            alternative_label_node = AlternativeLabel(label=label).save()
            node.alternative_label.connect(alternative_label_node)
            embedding = request_embedding(label)
            embedding_node = EMBEDDING_MODEL_MAPPER[self.label](vector=embedding, input=label).save()
            node.model_embedding.connect(embedding_node)
        embedding_node = EMBEDDING_MODEL_MAPPER[self.label](vector=request_embedding(node.name), input=node.name).save()
        node.model_embedding.connect(embedding_node)

    def ontology_extension_prompt(self, input, ontology):
        return f"Input: {input}\nContext: {self.context}\nCandidates: {', '.join([ont[0].name for ont in ontology])}"

    def create_synonym(self, input, ontology, label):
        prompt = self.ontology_extension_prompt(input, ontology)
        output = chat_with_gpt3(prompt=prompt, setup_message=SETUP_MESSAGES[label])
        return output

    def extend_ontology(self, input, ontology, label):
        ontology_node = ONTOLOGY_MAPPER[label](name=input)
        self.save_ontology_node(ontology_node)
        return ontology_node

    def run(self):
        self.map_on_ontology()
