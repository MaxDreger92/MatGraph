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
        self.row = [element['column_values'][0] if element['column_values'] else '' for element in data]
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
        setup_message = self.setup_message

        # Send the initial query to ChatGPT and get the initial response
        query_result = chat_with_gpt4(setup_message, query)
        print("Query Result:", query_result)
        self.create_node_list(query_result)
        self.conversation = [*self.conversation,{"role": "user", "content": query}, {"role": "system", "content": query_result[0]}]

    def create_node_list(self, string):
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
                    node['id'] = f"inferred_{self.label}_{i}"
                else:
                    node['id'] = str(node['name'][0][1])
                keys_to_keep  = ['label', 'id', 'attributes']

                updated_node = {'name': [{'value': name[0], 'index': name[1]} for name in node['name']],
                    'attributes': {key: value for key, value in node.items() if key not in ['label', 'id']},
                    ** {key: value for key, value in node.items() if key in keys_to_keep}
                }
                self.node_list[i] = updated_node
            for i, node in enumerate(self.node_list):
                updated_attributes = {}
                for key, value in node['attributes'].items():
                    if isinstance(value[0], list):
                        updated_attributes[key] = []
                        for attribute in value:
                            updated_attributes[key].append({'value': attribute[0], 'index': attribute[1]})
                    else:
                        print("value", value)
                        updated_attributes[key] = {'value': value[0], 'index': value[1]}
                self.node_list[i]['attributes'] = updated_attributes
            print("Changed Node List:", self.node_list)


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
        self.label = "matter"

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
        self.label = "property"

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
        self.label = "parameter"

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
        self.label = "manufacturing"


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
        self.label = "measurement"

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
        self.label = "metadata"





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
        with ThreadPoolExecutor() as executor:
            # Create a list of future tasks
            future_to_aggregator = {executor.submit(aggregator.run): aggregator for aggregator_type, aggregator_class in [
                ("Matter", MatterAggregator),
                ("Property", PropertyAggregator),
                ("Parameter", ParameterAggregator),
                ("Manufacturing", ManufacturingAggregator),
                ("Measurement", MeasurementAggregator)
            ] for aggregator in self.process_aggregator(aggregator_type, aggregator_class)}

            # As each task completes, extend the node list
            for future in as_completed(future_to_aggregator):
                aggregator = future_to_aggregator[future]
                self.node_list.extend(aggregator.node_list)
            self.node_list = {"nodes": self.node_list, "relationships": []}



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
    def build_results(self):
        self._results = self.node_list

    def run(self):
        self.get_table_understanding()
        self.build_results()




