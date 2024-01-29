import json
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint

from importing.NodeExtraction.setupMessages import MATTER_AGGREGATION_MESSAGE, PROPERTY_AGGREGATION_MESSAGE, \
    PARAMETER_AGGREGATION_MESSAGE, MANUFACTURING_AGGREGATION_MESSAGE, MEASUREMENT_AGGREGATION_MESSAGE
from importing.utils.openai import chat_with_gpt4

from graphutils.general import TableDataTransformer
from importing.models import NodeExtractionReport



class NodeAggregator:
    def __init__(self, data, context, setup_message, additional_context):
        self.header = [f"{element['header']} ({element['attribute']}, {element['index']})" for element in data]
        self.row = [element['column_values'][0] for element in data]
        self.setup_message = setup_message
        self.context = context
        self.additional_context = additional_context
        self.conversation = self.setup_message
        self.label = None

    def create_query(self):
        return f"""
        Context: {self.context}
    
        Table:
        {", ".join(self.header)}
        {", ".join(self.row)}
        
        {self.additional_context}
        """


    def validate(self):
        pass

    def aggregate(self, query):
        print("Query to GPT-4:")
        print(query)
        setup_message = self.setup_message

        # Send the initial query to ChatGPT and get the initial response
        query_result = chat_with_gpt4(setup_message, query)
        self.create_node_list(query_result)
        print("GPT-4 Initial Response:")
        self.conversation = [*self.conversation,{"role": "user", "content": query}, {"role": "system", "content": query_result[0]}]

    def create_node_list(self, string):
        print("Original String:", string)
        # Preprocess the string
        processed_string = string
        pattern = r'```python\s+(.*?)\s+```'
        processed_string = re.search(pattern, processed_string, re.DOTALL).group(1)

        # Replace single backslashes with double backslashes
        processed_string = processed_string.replace('\\', '\\\\')

        # Try to load the JSON to check for errors
        try:
            self.node_list = json.loads(processed_string, strict = False)
            for i, node in enumerate(self.node_list):
                node['label'] = self.label
                if node['name'][0][1] == "inferred":
                    node['node_id'] = f"inferred_{self.label}_{i}"
                else:
                    node['node_id'] = node['name'][0][1]
                keys_to_keep  = ['label', 'node_id', 'name', 'attributes']

                updated_node = {
                    'attributes': {key: value for key, value in node.items() if key not in ['label', 'node_id']},
                    ** {key: value for key, value in node.items() if key in keys_to_keep}
                }
                self.node_list[i] = updated_node


            print("JSON Loaded Successfully")
        except json.JSONDecodeError as e:
            print("Error parsing JSON:", str(e))
            # Handle the error or return None to indicate failure


    def run(self):
        query = self.create_query()
        self.aggregate(query)
        self.validate()





class MatterAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message = MATTER_AGGREGATION_MESSAGE,
                 additional_context = """REMEMBER:
    
                - Extract all distinguishable  Materials, Components, Devices, Chemicals, Intermediates, Products, Layers etc. from the table above.
                - If a node is fabricated by processing more than one educt, extract the product and the educt as separate nodes
                - If only one educt is used to fabricate a node, extract them as a single node
                - do not create duplicate nodes, if not necessary
                - assign concentrations and ratios to educts not to products
                - do not create nodes that have exactly the same name if the materials/components/devices they represent do not occur multiple times
                - only extract the attributes name, concentration, ratio, identifier, and batch number
                - only return the final list of nodes
                
                WHEN CREATING THE LIST OF NODES STRICTLY FOLLOW THE REASONING FROM STEP 1 AND STEP 2!
                """):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "Matter"

class PropertyAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message = PROPERTY_AGGREGATION_MESSAGE,
                 additional_context = """REMEMBER:
                WHEN CREATING THE LIST OF NODES STRICTLY FOLLOW THE REASONING FROM STEP 1 AND STEP 2!
                ONLY RETURN THE FINAL LIST OF NODES!
                """):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "Property"

    def create_node_list(self, string):
        super.create_node_list(string)
        for node in self.node_list:
            if "measurement_condition" in node.keys():
                parameter_node = {
                    "label": "Parameter",
                    **node['measurement_condition']
                }
                self.node_list.append(parameter_node)


class ParameterAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message = PARAMETER_AGGREGATION_MESSAGE,
                 additional_context = """REMEMBER:
                WHEN CREATING THE LIST OF NODES STRICTLY FOLLOW THE REASONING FROM STEP 1 AND STEP 2!
                ONLY RETURN THE FINAL LIST OF NODES!
                """):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "Parameter"

class ManufacturingAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message = MANUFACTURING_AGGREGATION_MESSAGE,
                 additional_context = """REMEMBER:
                WHEN CREATING THE LIST OF NODES STRICTLY FOLLOW THE REASONING FROM STEP 1 AND STEP 2!
                ONLY RETURN THE FINAL LIST OF NODES!
                """):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "Manufacturing"


class MeasurementAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message = MEASUREMENT_AGGREGATION_MESSAGE,
                 additional_context = """REMEMBER:
                WHEN CREATING THE LIST OF NODES STRICTLY FOLLOW THE REASONING FROM STEP 1 AND STEP 2!
                ONLY RETURN THE FINAL LIST OF NODES!
                """):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "Measurement"

class MetadataAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message = PARAMETER_AGGREGATION_MESSAGE,
                 additional_context = """REMEMBER:
                WHEN CREATING THE LIST OF NODES STRICTLY FOLLOW THE REASONING FROM STEP 1 AND STEP 2!
                ONLY RETURN THE FINAL LIST OF NODES!
                """):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "Metadata"





class NodeExtractor(TableDataTransformer):


    def __init__(self, ReportClass = NodeExtractionReport,  **kwargs):
        self.node_list = []
        super().__init__(ReportClass = NodeExtractionReport, **kwargs)


    def group_by_prefix(self, data):
        grouped = defaultdict(list)
        for entry in data:
            prefix = entry['header'].split('_', 1)[0]
            grouped[prefix].append(entry)
        return grouped


    def process_aggregator(self, data_type, aggregator_class):
        if data_type in self.iterable and self.iterable[data_type]:
            data = self.iterable[data_type]
            if data_type == "Property":
                # Special handling for properties
                matter_list = ", ".join([", ".join([name[0] for name in matter['name']]) for matter in self.node_list])
                context = f"{self.context}. Here are materials and device candidates to which the following properties might belong: {matter_list}"
            else:
                context = self.context

            grouped_data = self.group_by_prefix(data) if data_type == "Property" else {None: data}
            for entries in grouped_data.values():
                aggregator = aggregator_class(entries, context)
                yield aggregator

    def get_table_understanding(self):
        # with ThreadPoolExecutor() as executor:
        #     # Create a list of future tasks
        #     future_to_aggregator = {executor.submit(aggregator.run): aggregator for aggregator_type, aggregator_class in [
        #         ("Matter", MatterAggregator),
        #         ("Property", PropertyAggregator),
        #         ("Parameter", ParameterAggregator),
        #         ("Manufacturing", ManufacturingAggregator),
        #         ("Measurement", MeasurementAggregator)
        #     ] for aggregator in self.process_aggregator(aggregator_type, aggregator_class)}
        #
        #     # As each task completes, extend the node list
        #     for future in as_completed(future_to_aggregator):
        #         aggregator = future_to_aggregator[future]
        #         self.node_list.extend(aggregator.node_list)
        #         self.node_list = {"nodes": self.node_list}
        self._results = {
                'nodes': [
                    {'label': 'Manufacturing', 'node_id': 0, 'name': [['Spincoating', 2]], 'attributes': {'name': [['Spincoating', 2]]}},
                    {'label': 'Manufacturing', 'node_id': 1, 'name': [['Spincoating', 16]], 'attributes': {'name': [['Spincoating', 16]]}},
                    {'label': 'Manufacturing', 'node_id': 2, 'name': [['Spincoating', 30]], 'attributes': {'name': [['Spincoating', 30]]}},
                    {'label': 'Manufacturing', 'node_id': 3, 'name': [['Spincoating', 44]], 'attributes': {'name': [['Spincoating', 44]]}},
                    {'label': 'Manufacturing', 'node_id': 4, 'name': [['Spincoating', 58]], 'attributes': {'name': [['Spincoating', 58]]}},
                    {'label': 'Manufacturing', 'node_id': 5, 'name': [['Evaporation', 72]], 'attributes': {'name': [['Evaporation', 72]]}},
                    {'label': 'Manufacturing', 'node_id': 6, 'name': [['Evaporation', 86]], 'attributes': {'name': [['Evaporation', 86]]}},
                    {'label': 'Matter', 'node_id': 7, 'name': [['ETL', 1]], 'attributes': {'name': [['ETL', 1]], 'identifier': [['13841', 0]], 'ratio': [['1', 8]]}},
                    {'label': 'Matter', 'node_id': 8, 'name': [['ZnO', 11]], 'attributes': {'name': [['ZnO', 11]], 'material_batch_barcode': [['121800', 10]]}},
                    {'label': 'Matter', 'node_id': 9, 'name': [['ActiveLayer', 15]], 'attributes': {'name': [['ActiveLayer', 15]], 'identifier': [['13841', 14]]}},
                    {'label': 'Matter', 'node_id': 10, 'name': [['Donor', 23]], 'attributes': {'name': [['Donor', 23]], 'ratio': [['0.8112', 22]]}},
                    {'label': 'Matter', 'node_id': 11, 'name': [['PM6', 25]], 'attributes': {'name': [['PM6', 25]], 'concentration': [['19.8846153846154', 18]], 'material_batch_barcode': [['321100', 24]]}},
                    {'label': 'Matter', 'node_id': 12, 'name': [['Acceptor', 37]], 'attributes': {'name': [['Acceptor', 37]], 'ratio': [['0.2128', 36]]}},
                    {'label': 'Matter', 'node_id': 13, 'name': [['Y12', 39]], 'attributes': {'name': [['Y12', 39]], 'concentration': [['19.4615384615385', 32]], 'material_batch_barcode': [['321116', 38]]}},
                    {'label': 'Matter', 'node_id': 14, 'name': [['Acceptor', 51]], 'attributes': {'name': [['Acceptor', 51]], 'ratio': [['0.0234', 50]]}},
                    {'label': 'Matter', 'node_id': 15, 'name': [['PCBM70', 53]], 'attributes': {'name': [['PCBM70', 53]], 'concentration': [['27.5000000000001', 46]], 'material_batch_barcode': [['321046', 52]]}},
                    {'label': 'Matter', 'node_id': 16, 'name': [['Solvent', 65]], 'attributes': {'name': [['Solvent', 65]], 'ratio': [['1', 64]]}},
                    {'label': 'Matter', 'node_id': 17, 'name': [['o-Xylene', 67]], 'attributes': {'name': [['o-Xylene', 67]], 'concentration': [['27.5000000000001', 60]], 'material_batch_barcode': [['5', 66]]}},
                    {'label': 'Matter', 'node_id': 18, 'name': [['HTL', 71]], 'attributes': {'name': [['HTL', 71]], 'identifier': [['13841', 70]]}},
                    {'label': 'Matter', 'node_id': 19, 'name': [['MoOx', 81]], 'attributes': {'name': [['MoOx', 81]], 'material_batch_barcode': [['7', 80]]}},
                    {'label': 'Matter', 'node_id': 20, 'name': [['Electrode', 85]], 'attributes': {'name': [['Electrode', 85]], 'identifier': [['13841', 84]]}},
                    {'label': 'Matter', 'node_id': 21, 'name': [['Ag', 95]], 'attributes': {'name': [['Ag', 95]], 'material_batch_barcode': [['6', 94]]}},
                    {'label': 'Parameter', 'node_id': 22, 'name': [['annealing_time', 'inferred']], 'attributes': {'name': [['annealing_time', 'inferred']], 'unit': [['h:min:s', 'inferred']], 'value': [['00:46:01', 12]]}},
                    {'label': 'Parameter', 'node_id': 23, 'name': [['annealing_temperature', 'inferred']], 'attributes': {'name': [['annealing_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['180', 13]]}},
                    {'label': 'Parameter', 'node_id': 24, 'name': [['layer_material_temperature', 'inferred']], 'attributes': {'name': [['layer_material_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['25', 19]]}},
                    {'label': 'Parameter', 'node_id': 25, 'name': [['layer_material_stirring_time', 'inferred']], 'attributes': {'name': [['layer_material_stirring_time', 'inferred']], 'unit': [['s', 'inferred']], 'value': [['100', 20]]}},
                    {'label': 'Parameter', 'node_id': 26, 'name': [['layer_material_stirring_speed', 'inferred']], 'attributes': {'name': [['layer_material_stirring_speed', 'inferred']], 'unit': [['rpm', 'inferred']], 'value': [['600', 21]]}},
                    {'label': 'Parameter', 'node_id': 27, 'name': [['annealing_time', 'inferred']], 'attributes': {'name': [['annealing_time', 'inferred']], 'unit': [['h:min:s', 'inferred']], 'value': [['00:10:15', 26]]}},
                    {'label': 'Parameter', 'node_id': 28, 'name': [['annealing_temperature', 'inferred']], 'attributes': {'name': [['annealing_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['160', 27]]}},
                    {'label': 'Parameter', 'node_id': 29, 'name': [['layer_material_temperature', 'inferred']], 'attributes': {'name': [['layer_material_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['24', 33]]}},
                    {'label': 'Parameter', 'node_id': 30, 'name': [['layer_material_stirring_time', 'inferred']], 'attributes': {'name': [['layer_material_stirring_time', 'inferred']], 'unit': [['s', 'inferred']], 'value': [['240', 34]]}},
                    {'label': 'Parameter', 'node_id': 31, 'name': [['layer_material_stirring_speed', 'inferred']], 'attributes': {'name': [['layer_material_stirring_speed', 'inferred']], 'unit': [['rpm', 'inferred']], 'value': [['500', 35]]}},
                    {'label': 'Parameter', 'node_id': 32, 'name': [['annealing_time', 'inferred']], 'attributes': {'name': [['annealing_time', 'inferred']], 'unit': [['h:min:s', 'inferred']], 'value': [['00:10:15', 40]]}},
                    {'label': 'Parameter', 'node_id': 33, 'name': [['annealing_temperature', 'inferred']], 'attributes': {'name': [['annealing_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['250', 41]]}},
                    {'label': 'Parameter', 'node_id': 34, 'name': [['layer_material_temperature', 'inferred']], 'attributes': {'name': [['layer_material_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['20', 47]]}},
                    {'label': 'Parameter', 'node_id': 35, 'name': [['layer_material_stirring_time', 'inferred']], 'attributes': {'name': [['layer_material_stirring_time', 'inferred']],        'unit': [['s', 'inferred']], 'value': [['160', 48]]}},
                    {'label': 'Parameter', 'node_id': 36, 'name': [['layer_material_stirring_speed', 'inferred']], 'attributes': {'name': [['layer_material_stirring_speed', 'inferred']], 'unit': [['rpm', 'inferred']], 'value': [['500', 49]]}},
                    {'label': 'Parameter', 'node_id': 37, 'name': [['annealing_time', 'inferred']], 'attributes': {'name': [['annealing_time', 'inferred']], 'unit': [['h:min:s', 'inferred']], 'value': [['00:10:15', 54]]}},
                    {'label': 'Parameter', 'node_id': 38, 'name': [['annealing_temperature', 'inferred']], 'attributes': {'name': [['annealing_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['288', 55]]}},
                    {'label': 'Parameter', 'node_id': 39, 'name': [['layer_material_temperature', 'inferred']], 'attributes': {'name': [['layer_material_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['22', 61]]}},
                    {'label': 'Parameter', 'node_id': 40, 'name': [['layer_material_stirring_time', 'inferred']], 'attributes': {'name': [['layer_material_stirring_time', 'inferred']], 'unit': [['s', 'inferred']], 'value': [['240', 62]]}},
                    {'label': 'Parameter', 'node_id': 41, 'name': [['layer_material_stirring_speed', 'inferred']], 'attributes': {'name': [['layer_material_stirring_speed', 'inferred']], 'unit': [['rpm', 'inferred']], 'value': [['1600', 63]]}},
                    {'label': 'Parameter', 'node_id': 42, 'name': [['annealing_time', 'inferred']], 'attributes': {'name': [['annealing_time', 'inferred']], 'unit': [['h:min:s', 'inferred']], 'value': [['00:10:15', 68]]}},
                    {'label': 'Parameter', 'node_id': 43, 'name': [['annealing_temperature', 'inferred']], 'attributes': {'name': [['annealing_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['120', 69]]}},
                    {'label': 'Parameter', 'node_id': 44, 'name': [['annealing_time', 'inferred']], 'attributes': {'name': [['annealing_time', 'inferred']], 'unit': [['h:min:s', 'inferred']], 'value': [['00:20:47', 82]]}},
                    {'label': 'Parameter', 'node_id': 45, 'name': [['annealing_temperature', 'inferred']], 'attributes': {'name': [['annealing_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['100', 83]]}},
                    {'label': 'Parameter', 'node_id': 46, 'name': [['annealing_time', 'inferred']], 'attributes': {'name': [['annealing_time', 'inferred']], 'unit': [['h:min:s', 'inferred']], 'value': [['00:20:47', 96]]}},
                    {'label': 'Parameter', 'node_id': 47, 'name': [['annealing_temperature', 'inferred']], 'attributes': {'name': [['annealing_temperature', 'inferred']], 'unit': [['C', 'inferred']], 'value': [['100', 97]]}}
                ],
            "relationships": []
        }

        print("Node List:")
        pprint(self.node_list, indent = 3)


    @property
    def iterable(self):
        # Group elements by label.
        grouped_by_label = defaultdict(list)
        for index, element in enumerate(self.data):
            label = element['1_label']
            grouped_by_label[label].append(element)


        # Sort the dictionary by label.
        sorted_grouped_by_label = dict(sorted(grouped_by_label.items()))

        # Modify data for sorted groups.
        modified_data = {key: [
            {
                'header': element['header'],
                'column_values': element['column_values'][:3],
                'attribute': element.get('1_attribute'),
                'index': element.get('index')
            }
            for index, element in enumerate(value)
        ]
            for key, value in sorted_grouped_by_label.items()}
        return modified_data

    def _pre_check(self, element, **kwargs):
        if element['attribute'] is None:
            return True
        return False

    def run(self):
        self.get_table_understanding()




