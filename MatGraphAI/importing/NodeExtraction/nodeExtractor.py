from collections import defaultdict
from pprint import pprint

from importing.NodeExtraction.setupMessages import CONTEXT_GENERATION_MESSAGE
from importing.utils.openai import chat_with_gpt4

from graphutils.general import TableDataTransformer
from importing.models import NodeExtractionReport


class NodeExtractor(TableDataTransformer):


    def __init__(self, ReportClass = NodeExtractionReport,  **kwargs):
        super().__init__(ReportClass = NodeExtractionReport, **kwargs)


    def get_table_understanding(self):
        # Existing process to generate the initial query and get response
        data = self.iterable['Matter']
        header = [element['header'] for element in data]
        header_table = [element['header'] + f" ({element['attribute']})" for element in data]
        row = [element['column_values'][0] for element in data]
        header_row = [{'column_header': element['header'], 'column_value': element['column_values'][0], 'attribute_type': element['attribute'], "index": element["index"]} for element in data]
        query = f"""
    Context: {self.context}
    
    Table: 
    {", ".join(header_table)}
    {", ".join(row)}
    
    REMEMBER:
    
    - Extract all distinguishable  Materials, Components, Devices, Chemicals, Intermediates, Products, Layers etc. from the table above.
    - If a node is fabricated by processing more than one educt, extract the product and the educt as separate nodes
    - If only one educt is used to fabricate a node, extract them as a single node
    - do not create duplicate nodes, if not necessary
    - assign concentrations and ratios to educts not to products
    - do not create nodes that have exactly the same name if the materials/components/devices they represent do not occur multiple times
    """

        print("Query to GPT-4:")
        print(query)
        setup_message = CONTEXT_GENERATION_MESSAGE

        # Send the initial query to ChatGPT and get the initial response
        query_result = chat_with_gpt4(setup_message, query)

        # Print the initial response
        print("\nGPT-4 Initial Response:")
        for res in query_result:
            print(res)
        conversation = [*setup_message,{"role": "user", "content": query}, {"role": "system", "content": query_result[0]}]

        # Now, you can continue the conversation by asking additional prompts
        while True:
            user_prompt = input("Your prompt to GPT-4 (or enter 'exit' to end the conversation): ")

            if user_prompt.lower() == 'exit':
                break

            # Send the user's prompt to ChatGPT
            query_result = chat_with_gpt4(conversation, user_prompt)

            # Print the response
            print("\nGPT-4 Response:")
            for res in query_result:
                print(res)
            conversation.append({"role": "user", "content": user_prompt})
            conversation.append({"role": "system", "content": query_result[0]})



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


