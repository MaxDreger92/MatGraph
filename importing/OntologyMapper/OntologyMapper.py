import ast
import csv
import json
from io import StringIO

from dbcommunication.ai.setupMessages import MATTER_ONTOLOGY_CANDIDATES_MESSAGES, PROCESS_ONTOLOGY_CANDIDATES_MESSAGES, \
    QUANTITY_ONTOLOGY_CANDIDATES_MESSAGES, QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES, PROCESS_ONTOLOGY_ASSISTANT_MESSAGES, \
    MATTER_ONTOLOGY_ASSISTANT_MESSAGES, MATTER_ONTOLOGY_CONNECTOR_MESSAGES, PROCESS_ONTOLOGY_CONNECTOR_MESSAGES, \
    QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES
from graphutils.embeddings import request_embedding
from graphutils.models import AlternativeLabel
from importing.OntologyMapper.setupMessages import PARAMETER_SETUP_MESSAGE, MEASUREMENT_SETUP_MESSAGE, \
    MANUFACTURING_SETUP_MESSAGE, MATTER_SETUP_MESSAGE, PROPERTY_SETUP_MESSAGE
from importing.utils.openai import chat_with_gpt3, chat_with_gpt4
from matgraph.models.embeddings import MatterEmbedding, ProcessEmbedding, QuantityEmbedding
from matgraph.models.metadata import File
from matgraph.models.ontology import EMMOMatter, EMMOProcess, EMMOQuantity


from io import StringIO
import csv


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



ONTOLOGY_CANDIDATES = {
    'EMMOMatter': MATTER_ONTOLOGY_CANDIDATES_MESSAGES,
    'EMMOProcess': PROCESS_ONTOLOGY_CANDIDATES_MESSAGES,
    'EMMOQuantity': QUANTITY_ONTOLOGY_CANDIDATES_MESSAGES
}

ONTOLOGY_CONNECTOR = {
    'matter': MATTER_ONTOLOGY_CONNECTOR_MESSAGES,
    'manufacturing': PROCESS_ONTOLOGY_CONNECTOR_MESSAGES,
    'measurement': PROCESS_ONTOLOGY_CONNECTOR_MESSAGES,
    'property': QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES,
    'parameter': QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES
}

SETUP_MAPPER = {
    'matter': MATTER_ONTOLOGY_ASSISTANT_MESSAGES,
    'manufacturing': PROCESS_ONTOLOGY_ASSISTANT_MESSAGES,
    'measurement': PROCESS_ONTOLOGY_ASSISTANT_MESSAGES,
    'property': QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES,
    'parameter': QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES
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
        if name['index'] == 'inferred' and name['value'] not in self.names:
            self._append_mapping(name['value'], label)
        elif label != 'metadata':
            self._handle_table_mapping(name, label)

    def _handle_table_mapping(self, name, label):
        for col_value in self.table[int(name['index'])]:
            if col_value not in self.names:
                self._append_mapping(col_value, label)

    def _append_mapping(self, name_value, label):
        ontology_generator = OntologyGenerator(self.context, name_value, label, ONTOLOGY_MAPPER[label])
        node_uid = ontology_generator.get_or_create(name_value, label).uid
        self._mapping.append({'name': name_value, 'id': node_uid, 'label': ONTOLOGY_MAPPER[label].__name__})
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


    def save_ontology_node(self, node, add_labels_create_embeddings=True, connect_to_ontology=True):
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
                    try:
                        current_node.save()
                    except Exception as e:
                        print(f"Error saving node '{name}': {e}")
                        continue  # Skip this node and move to the next one

                # Connect the current node to the previous one in the chain, if applicable
                if previous_node and previous_node != current_node:
                    try:
                        previous_node.emmo_parentclass.connect(current_node)
                    except Exception as e:
                        print(f"Error connecting '{previous_node.name}' to '{current_node.name}': {e}")

                previous_node = current_node



    def find_candidates(self, node):
        nodes = self.ontology_class.nodes.get_by_string(string = node.name, limit = 8, include_similarity = False)
        prompt = f"""Input: {node.name}\nCandidates: {", ".join([node.name for node in nodes if node.name != node.name])} \nOnly return the final output!"""
        ontology_advice = chat_with_gpt4(prompt= prompt, setup_message= ONTOLOGY_CANDIDATES[self.ontology_class._meta.object_name])
        if ontology_advice.lower().strip(" ").strip("\n") == "false":
            uids = list(dict.fromkeys([node.uid for node in nodes if node.name != self.name]))
            return node.get_superclasses(uids)
        else:
            gpt_json = json.loads(ontology_advice.replace("\n", ""))
            if gpt_json['input_is_subclass_of_candidate']:
                candidate_uid = nodes[[node.name for node in nodes].index(gpt_json['candidate'])].uid
                return node.get_subclasses([candidate_uid])
            else:
                candidate_uid = nodes[[node.name for node in nodes].index(gpt_json['candidate'])].uid
                return node.get_superclasses([candidate_uid])

    def find_connection(self, candidates):
        prompt = f"""Input: {self.name}\nCandidates: {", ".join([candidate[1] for candidate in candidates])} \nOnly Return The Final List!"""
        connecting_path = chat_with_gpt4(prompt= prompt, setup_message= ONTOLOGY_CONNECTOR[self.label])
        return ast.literal_eval(connecting_path)

    def add_labels_create_embeddings(self, node):
        alternative_labels = chat_with_gpt4(prompt= node.name, setup_message= SETUP_MAPPER[self.label])
        alternative_labels = json.loads(alternative_labels)
        for label in alternative_labels['alternative_labels']:
            alternative_label_node = AlternativeLabel(label = label).save()
            node.alternative_label.connect(alternative_label_node)
            embedding = request_embedding(label)
            embedding_node = EMBEDDING_MODEL_MAPPER[self.label](vector = embedding, input = label).save()
            node.model_embedding.connect(embedding_node)
        embedding_node = EMBEDDING_MODEL_MAPPER[self.label](vector = request_embedding(node.name), input = node.name).save()
        node.model_embedding.connect(embedding_node)

    def get_or_create(self, input, label):
        ontology = ONTOLOGY_MAPPER[label].nodes.get_by_string(string=input, limit=15, include_similarity=True)
        print(f"Checking {input}")
        if ontology[0][1] < 0.97:
            print(f"Extension required")
            return self.extend_ontology(input, ontology, label)
        else:
            print(f"High similarity found")
            return ontology[0][0]

    def ontology_extension_prompt(self, input, ontology):
        return f"Input: {input}\nContext: {self.context}\nCandidates: {', '.join([ont[0].name for ont in ontology])}"

    def create_synonym(self, input, ontology, label):
        prompt = self.ontology_extension_prompt(input, ontology)
        output = chat_with_gpt3(prompt=prompt, setup_message=SETUP_MESSAGES[label])
        return output

    def extend_ontology(self, input, ontology, label):
        output = self.create_synonym(input, ontology, label)
        nodes = ONTOLOGY_MAPPER[label].nodes.get_by_string(string=output, limit=15, include_similarity=True)
        if nodes[0][1] < 0.97:
            print(f"still no match, creating new node")
            print(label, input, output)
            ontology_node = ONTOLOGY_MAPPER[label](name=output)
            self.save_ontology_node(ontology_node)
            return ontology_node
        else:
            print(f"found match, returning node")
            return nodes[0][0]

    def run(self):
        self.map_on_ontology()
