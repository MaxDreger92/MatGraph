import csv
from asyncio import sleep
from io import StringIO

from importing.OntologyMapper.setupMessages import PARAMETER_SETUP_MESSAGE, MEASUREMENT_SETUP_MESSAGE, \
    MANUFACTURING_SETUP_MESSAGE, MATTER_SETUP_MESSAGE, PROPERTY_SETUP_MESSAGE
from importing.utils.openai import chat_with_gpt3, chat_with_gpt4
from matgraph.models.metadata import File
from matgraph.models.ontology import EMMOMatter, EMMOProcess, EMMOQuantity


class OntologyMapper:



    ONTOLOGY_MAPPER = {
        'matter': EMMOMatter,
        'manufacturing': EMMOProcess,
        'measurement': EMMOProcess,
        'parameter': EMMOQuantity,
        'property': EMMOQuantity
    }

    SETUP_MASSAGES = {
        'matter': MATTER_SETUP_MESSAGE,
        'manufacturing': MANUFACTURING_SETUP_MESSAGE,
        'measurement': MEASUREMENT_SETUP_MESSAGE,
        'parameter': PARAMETER_SETUP_MESSAGE,
        'property': PROPERTY_SETUP_MESSAGE
    }


    def __init__(self, data, file_link, context):
        self.data = data
        self.file_link = file_link
        self.context = context
        self._mapping = {}
        file = File.nodes.get(link=file_link)
        file_obj_bytes = file.get_file()

        # Decode the bytes object to a string
        file_obj_str = file_obj_bytes.decode('utf-8')


        # Use StringIO on the decoded string
        file_obj = StringIO(file_obj_str)
        csv_reader = csv.reader(file_obj)
        first_row = next(csv_reader)

        column_values = [[] for _ in range(len(first_row))]

        for row in csv_reader:
            for i, value in enumerate(row):
                column_values[i].append(value)

        self._table = column_values

    @property
    def table(self):
        return self._table

    @property
    def mapping(self):
        return self._mapping

    def map_on_ontology(self):
        for i, node in enumerate(self.data['nodes']):
            if type(node['name']) != list:
                node['name'] = [node['name']]
            label = node['label']
            for j, name in enumerate(node['name']):
                if name['index'] == 'inferred':
                    if name['value'] not in self._mapping:
                        node_uid = self.get_label(name['value'], label)
                        self._mapping[name['value']] = {'id': node_uid, 'label': self.ONTOLOGY_MAPPER[label].__name__}
                        continue
                else:
                    if label != 'metadata':
                        table_column = self.table[int(name['index'])]
                        for col_value in table_column:
                            if col_value == '' or col_value is None:
                                continue

                            # Check if the mapping for col_value already exists
                            if col_value not in self.mapping:
                                node_uid = self.get_label(col_value, label)
                                self._mapping[col_value] = {'id': node_uid, 'label': self.ONTOLOGY_MAPPER[label].__name__}
                            else:
                                continue
        print("CREATED MAPPING", self.mapping)

    def get_label(self, input, label):
        ontology = self.ONTOLOGY_MAPPER[label].nodes.get_by_string(string = input, limit = 8, include_similarity = True)
        if ontology[0][1] < 0.97:
            print(f"did not find label for {input}")
            return self.extend_ontology(input, ontology, label)
        else:
            print(f"found label for {input}: {ontology[0][0].name} {ontology[0][1]} {ontology[0][2]}")
            # ontology[0][0].connect_to_ontology()
            return ontology[0][0].uid

    def extend_ontology(self, input, ontology, label):
        prompt = "Input: " + input + "\nContext: " + self.context + "\nCandidates: " + ', '.join([ont[0].name for ont in ontology])
        output = chat_with_gpt3(prompt= prompt, setup_message= self.SETUP_MASSAGES[label])
        nodes = self.ONTOLOGY_MAPPER[label].nodes.get_by_string(string = output, limit = 15, include_similarity = True)
        if nodes[0][1] < 0.97:
            print(f"did not find label for {output}")
            ontology_node = self.ONTOLOGY_MAPPER[label](name = output).save()
            return ontology_node.uid
        else:
            print(f"found label for {output}: {nodes[0][0].name} {nodes[0][1]}")
            return nodes[0][0].uid

    def run(self):
        # self.map_on_ontology()
        self._mapping = {'Spincoating': {'id': 'f0d464a496fe4beeb54d8957311a44b4', 'label': 'EMMOProcess'}, 'Evaporation': {'id': 'd4b87963f1d449b6b3c1d17fb96393f0', 'label': 'EMMOProcess'}, 'layer_material_temperature': {'id': 'd4c04631010d4b219309ee2f5f81b594', 'label': 'EMMOQuantity'}, 'layer_material_stirring_time': {'id': '4bf3c3677bd14d9683013cb0f2b28953', 'label': 'EMMOQuantity'}, 'layer_material_stirring_speed': {'id': '4009fce40034417e905d4b39d96ad04e', 'label': 'EMMOQuantity'}, 'annealing_time': {'id': 'ad9b714942c9444facc20482e97cc0f5', 'label': 'EMMOQuantity'}, 'annealing_temperature': {'id': 'ad9b714942c9444facc20482e97cc0f5', 'label': 'EMMOQuantity'}, 'SolarCell': {'id': 'eea92a0d8b054d55b1894ce172ab1aa4', 'label': 'EMMOMatter'}, 'ETL': {'id': '4f2fb032bb344ed7b3af45f7518ce21e', 'label': 'EMMOMatter'}, 'ZnO': {'id': '1a7af843d6454624b8fd96d89b7e1abb', 'label': 'EMMOMatter'}, 'ActiveLayer': {'id': '8ef660edb64744c3838ecaac7cd9fae3', 'label': 'EMMOMatter'}, 'Donor': {'id': 'a618d92ebe3a43a08b99911e115a09fc', 'label': 'EMMOMatter'}, 'Acceptor': {'id': 'acc47a72a5b84edba9098cbfa9d5e248', 'label': 'EMMOMatter'}, 'PM6': {'id': 'cbaafb9ae4f44f589138b184046863a4', 'label': 'EMMOMatter'}, 'Y12': {'id': 'c4bc70d9d16449ecbc1242b6a7ddd603', 'label': 'EMMOMatter'}, 'Solvent': {'id': '73d29791947f4503992a85012764886f', 'label': 'EMMOMatter'}, 'PCBM70': {'id': 'f4deb040f7214e51b38abf83c6030936', 'label': 'EMMOMatter'}, 'o-Xylene': {'id': '0dc58d4f92bb42079634ba54a0b48d15', 'label': 'EMMOMatter'}, 'HTL': {'id': '4f2fb032bb344ed7b3af45f7518ce21e', 'label': 'EMMOMatter'}, 'MoOx': {'id': 'f16a4c9b6c8d42d3a2d00ed96746628c', 'label': 'EMMOMatter'}, 'Electrode': {'id': '6c51334c5ed54105936e104e7434f4e0', 'label': 'EMMOMatter'}, 'Ag': {'id': '18299d51bf0340a3823c6f6d99e945ec', 'label': 'EMMOMatter'}}
        converted_list =[]
        for key, value in self._mapping.items():
            # Copy the original dictionary to avoid modifying it
            new_item = value.copy()
            # Add the original key under a new key name, e.g., 'key'
            new_item['key'] = key
            # Append the modified dictionary to the list
            converted_list.append(new_item)
        self._mapping = converted_list
        print("MAPPING", converted_list)
        print(str(converted_list).replace("':", ":").replace("{'", "{").replace(", '", ", ").replace("-", "_"))
