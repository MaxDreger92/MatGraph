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
    def map_on_ontology(self):
        mapping = {}
        for i, node in enumerate(self.data['nodes']):
            if type(node['name']) != list:
                node['name'] = [node['name']]
            label = node['label']
            for j, name in enumerate(node['name']):
                if name['index'] == 'inferred':
                    if name['value'] not in mapping:
                        node_name = self.get_label(name['value'], label)
                        mapping[name['value']] = node_name
                        continue
                else:
                    if label != 'metadata':
                        table_column = self.table[int(name['index'])]
                        for col_value in table_column:
                            if col_value == '' or col_value is None:
                                continue

                            # Check if the mapping for col_value already exists
                            if col_value not in mapping:
                                node_name = self.get_label(col_value, label)
                                mapping[col_value] = node_name
                            else:
                                continue

    def get_label(self, input, label):
        ontology = self.ONTOLOGY_MAPPER[label].nodes.get_by_string(string = input, limit = 8, include_similarity = True)
        if ontology[0][1] < 0.97:
            print(f"did not find label for {input}")
            return self.extend_ontology(input, ontology, label)
        else:
            print(f"found label for {input}: {ontology[0][0].name} {ontology[0][1]} {ontology[0][2]}")
            # ontology[0][0].connect_to_ontology()
            pass

    def extend_ontology(self, input, ontology, label):
        prompt = "Input: " + input + "\nContext: " + self.context + "\nCandidates: " + ', '.join([ont[0].name for ont in ontology])
        output = chat_with_gpt3(prompt= prompt, setup_message= self.SETUP_MASSAGES[label])
        nodes = self.ONTOLOGY_MAPPER[label].nodes.get_by_string(string = output, limit = 15, include_similarity = True)
        if nodes[0][1] < 0.97:
            print(f"did not find label for {output}")
            ontology_node = self.ONTOLOGY_MAPPER[label](name = output).save()
            return ontology_node
        else:
            print(f"found label for {output}: {nodes[0][0].name} {nodes[0][1]}")
            return nodes[0][0].name
