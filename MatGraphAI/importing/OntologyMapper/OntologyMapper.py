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

ONTOLOGY_MAPPER1 = {
    'EMMOMatter': MATTER_ONTOLOGY_ASSISTANT_MESSAGES,
    'EMMOProcess': PROCESS_ONTOLOGY_ASSISTANT_MESSAGES,
    'EMMOQuantity': QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES
}

EMBEDDING_MODEL_MAPPER = {
    'EMMOMatter': MatterEmbedding,
    'EMMOProcess': ProcessEmbedding,
    'EMMOQuantity': QuantityEmbedding
}



ONTOLOGY_CANDIDATES = {
    'EMMOMatter': MATTER_ONTOLOGY_CANDIDATES_MESSAGES,
    'EMMOProcess': PROCESS_ONTOLOGY_CANDIDATES_MESSAGES,
    'EMMOQuantity': QUANTITY_ONTOLOGY_CANDIDATES_MESSAGES
}

ONTOLOGY_CONNECTOR = {
    'EMMOMatter': MATTER_ONTOLOGY_CONNECTOR_MESSAGES,
    'EMMOProcess': PROCESS_ONTOLOGY_CONNECTOR_MESSAGES,
    'EMMOQuantity': QUANTITY_ONTOLOGY_CONNECTOR_MESSAGES
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
        operator = OntologyOperator(self.context, name_value, label, ONTOLOGY_MAPPER[label])
        node_uid = operator.get_label(name_value, label)
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


class OntologyOperator:

    def __init__(self, context, name, label, ontology_class):
        self.context = context
        self.name = name
        self.label = label
        self.ontology_class = ontology_class


    @staticmethod
    def save_ontology_node(node, add_labels_create_embeddings=True, connect_to_ontology=True):
        """
        Save an ontology node with the option to add labels, create embeddings, and connect to the ontology.

        :param node: The ontology node to save.
        :param add_labels_create_embeddings: Flag to add labels and create embeddings.
        :param connect_to_ontology: Flag to connect the node to the ontology.
        """
        node.save()  # Assuming node has a save method for basic saving operations
        print(f"saving {node.name}")
        if add_labels_create_embeddings:
            OntologyOperator.add_labels_create_embeddings(node)
        if connect_to_ontology:
            OntologyOperator.connect_to_ontology(node)

    @staticmethod
    def add_labels_create_embeddings(self):
        print(f"adding labels and embeddings for {self.name}")
        alternative_labels = chat_with_gpt4(prompt= self.name, setup_message= ONTOLOGY_MAPPER[self._meta.object_name])
        print(alternative_labels)
        alternative_labels = json.loads(alternative_labels)
        for label in alternative_labels['alternative_labels']:
            alternative_label_node = AlternativeLabel(label = label).save()
            self.alternative_label.connect(alternative_label_node)
            embedding = request_embedding(label)
            embedding_node = self.EMBEDDING_MODEL_MAPPER[self.__label__](vector = embedding, input = label).save()
            self.model_embedding.connect(embedding_node)
        embedding_node = self.EMBEDDING_MODEL_MAPPER[self.__label__](vector = request_embedding(self.name), input = self.name).save(add_labels_create_embeddings=True, connect_to_ontology=False)
        self.model_embedding.connect(embedding_node)
        self.validated_labels = False

    @staticmethod
    def connect_to_ontology(self):
        if len(self.emmo_subclass) == 0 and len(self.emmo_parentclass) == 0:
            candidates = self.find_candidates()
            find_connection = self.find_connection(candidates)
            previous_node = None
            for i, name in enumerate(find_connection):
                results = self.nodes.get_by_string(string=name, limit=8, include_similarity=True)
                if results and results[0][1] > 0.98:
                    node = results[0][0]  # Assuming the first element is the node
                else:
                    # Create new node if not found or similarity < 0.98
                    node = self.__class__(name= name)
                    node.save(add_labels_create_embeddings=True, connect_to_ontology=False)

                # Connect this node to the previous node in the chain with emmo_is_a relationship
                if previous_node and previous_node != node:
                    previous_node.emmo_parentclass.connect(node)
                previous_node = node



    def find_candidates(self):
        nodes = self.nodes.get_by_string(string = self.name, limit = 8, include_similarity = False)
        prompt = f"""Input: {self.name}\nCandidates: {", ".join([node.name for node in nodes if node.name != self.name])} \nOnly return the final output!"""
        ontology_advice = chat_with_gpt4(prompt= prompt, setup_message= ONTOLOGY_CANDIDATES[self._meta.object_name])
        if ontology_advice.lower().strip(" ").strip("\n") == "false":
            uids = list(dict.fromkeys([node.uid for node in nodes if node.name != self.name]))
            return self.get_superclasses(uids)
        else:
            gpt_json = json.loads(ontology_advice.replace("\n", ""))
            if gpt_json['input_is_subclass_of_candidate']:
                candidate_uid = nodes[[node.name for node in nodes].index(gpt_json['candidate'])].uid
                return self.get_subclasses([candidate_uid])
            else:
                candidate_uid = nodes[[node.name for node in nodes].index(gpt_json['candidate'])].uid
                return self.get_superclasses([candidate_uid])

    def find_connection(self, candidates):
        prompt = f"""Input: {self.name}\nCandidates: {", ".join([candidate[1] for candidate in candidates])} \nOnly Return The Final List!"""
        connecting_path = chat_with_gpt4(prompt= prompt, setup_message= ONTOLOGY_CONNECTOR[self.label])
        return ast.literal_eval(connecting_path)

    def add_labels_create_embeddings(self):
        alternative_labels = chat_with_gpt4(prompt= self.name, setup_message= ONTOLOGY_MAPPER[self.label])
        alternative_labels = json.loads(alternative_labels)
        for label in alternative_labels['alternative_labels']:
            alternative_label_node = AlternativeLabel(label = self.label).save()
            self.alternative_label.connect(alternative_label_node)
            embedding = request_embedding(self.label)
            embedding_node = EMBEDDING_MODEL_MAPPER[self.label](vector = embedding, input = label).save()
            self.model_embedding.connect(embedding_node)
        embedding_node = EMBEDDING_MODEL_MAPPER[self.label](vector = request_embedding(self.name), input = self.name).save()
        self.model_embedding.connect(embedding_node)

    def get_label(self, input, label):
        ontology = ONTOLOGY_MAPPER[label].nodes.get_by_string(string=input, limit=15, include_similarity=True)
        print(f"Checking {input}")
        if ontology[0][1] < 0.97:
            print(f"Extension required")
            return self.extend_ontology(input, ontology, label)
        else:
            print(f"High similarity found")
            return ontology[0][0].uid

    def extend_ontology(self, input, ontology, label):
        prompt = "Input: " + input + "\nContext: " + self.context + "\nCandidates: " + ', '.join(
            [ont[0].name for ont in ontology])
        output = chat_with_gpt3(prompt=prompt, setup_message=SETUP_MESSAGES[label])
        print(output, label, input)
        nodes = ONTOLOGY_MAPPER[label].nodes.get_by_string(string=output, limit=15, include_similarity=True)
        print(f"Used chatgpt to transform {input} to {output}")
        if nodes[0][1] < 0.97:
            print(f"still no match, creating new node")
            print(label, input, output)
            ontology_node = ONTOLOGY_MAPPER[label](name=output)
            ontology_node.save()
            print(ontology_node)
            return ontology_node.uid
        else:
            print(f"found match, returning uid")
            return nodes[0][0].uid

    def run(self):
        self.map_on_ontology()
