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
    # Existing process to generate the query and get response
        data = self.iterable['Matter']
        header = [element['header'] for element in data]
        row = [element['column_values'][0] for element in data]
        header_row = [{'column_header': element['header'], 'column_value': element['column_values'][0], 'attribute_type': element['attribute'], "index": element["index"]} for element in data]
        query = f"""
    Context: {self.context}
    
    Headers/Row: {header_row}
    
    Only give return the final output.
    """

        print("Query to GPT-4:")
        print(query)
        setup_message = CONTEXT_GENERATION_MESSAGE

        # Send the query to ChatGPT and get the response
        query_result = chat_with_gpt4(setup_message, query)

        # Print the response
        print("\nGPT-4 Response:")
        for res in query_result:
            print(res)



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


