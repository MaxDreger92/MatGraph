import json
import re
from collections import defaultdict
from pprint import pprint

from importing.NodeExtraction.setupMessages import MATTER_AGGREGATION_MESSAGE, PROPERTY_AGGREGATION_MESSAGE
from importing.utils.openai import chat_with_gpt4

from graphutils.general import TableDataTransformer
from importing.models import NodeExtractionReport



class NodeAggregator:
    def __init__(self, data, context, setup_message, additional_context):
        self.header = [f"{element['header']} ({element['attribute']})" for element in data]
        self.row = [element['column_values'][0] for element in data]
        self.setup_message = setup_message
        self.context = context
        self.additional_context = additional_context
        self.conversation = self.setup_message

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
        print("String:", string)
        self.node_list = json.loads(re.findall(r'\[\{.*\}\]', string, re.DOTALL)[0])
        print("NodeList:", self.node_list)


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
                
                WHEN CREATING THE LIST OF NODES STRICTLY FOLLOW THE REASONING FROM STEP 1 AND STEP 2!
                """):
        super().__init__(data, context, setup_message, additional_context)

class PropertyAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message = PROPERTY_AGGREGATION_MESSAGE,
                 additional_context = """REMEMBER:
                WHEN CREATING THE LIST OF NODES STRICTLY FOLLOW THE REASONING FROM STEP 1 AND STEP 2!
                """):
        super().__init__(data, context, setup_message, additional_context)



class NodeExtractor(TableDataTransformer):


    def __init__(self, ReportClass = NodeExtractionReport,  **kwargs):
        super().__init__(ReportClass = NodeExtractionReport, **kwargs)


    def get_table_understanding(self):
        # Existing process to generate the initial query and get response
        matter_aggregator = MatterAggregator(self.iterable["Matter"], self.context)
        matter_aggregator.run()




    @property
    def iterable(self):
        grouped_by_label = defaultdict(list)
        for index, element in enumerate(self.data):
            label = element.get('1_label')
            element['index'] = index
            grouped_by_label[label].append(element)

        modified_data = {key: [
            {
                'header': element['header'],
                'column_values': element['column_values'][:3],
                'attribute': element.get('1_attribute'),
                'index': element.get('index')
            }
            for index, element in enumerate(value)
        ]
        for key, value in grouped_by_label.items()}
        return modified_data

    def _pre_check(self, element, **kwargs):
        if element['attribute'] is None:
            return True
        return False

    def run(self):
        self.get_table_understanding()


