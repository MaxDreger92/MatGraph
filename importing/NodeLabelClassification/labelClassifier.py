import _io
import csv
import os
import re
import django

from graphutils.general import TableDataTransformer
from importing.NodeLabelClassification.setupMessages import CLASSIFY_PROPERTY_PARAMETERS
from importing.utils.openai import chat_with_gpt4, chat_with_gpt3

django.setup()

from quantulum3 import parser


from importing.models import LabelClassificationReport, NodeLabel, ImporterCache
import pandas as pd

class NodeClassifier(TableDataTransformer):
    """
    A classifier that processes a CSV file, extracts headers, and classifies them using a node label model.
    """
    def __init__(self, ReportClass = LabelClassificationReport,  **kwargs):
        self.attribute_type = "column_label"
        if type(kwargs['data']) == _io.StringIO:
            kwargs['data'].seek(0)
            kwargs['data'] = pd.read_csv(kwargs['data'], header=None)
        kwargs['data'] = [
            {
                'header': kwargs['data'].iloc[0, i],
                'column_values': column_values,
                'index': i,
            }
            for i in range(kwargs['data'].shape[1])
            if (column_values := kwargs['data'].iloc[1:, i].dropna().tolist())  # Assign and check in one line
        ]
        super().__init__(ReportClass = LabelClassificationReport, **kwargs)

    def contains_units(self, text):
        """
        Checks if the text contains any units.

        :param text: A string that may contain units.
        :return: Boolean indicating whether units are present.
        """
        quantities = parser.parse(text)
        return len(quantities) > 0



    def analyze_results(self, results, **kwargs):
        """
        Analyze the results to find the most occurring name and calculate its ratio to the total number of names.

        Parameters:
            results (list): A list of lists, where each inner list's first element is a node with an attribute 'name'.

        Returns:
            tuple: A tuple containing the most occurring name and its ratio to the total number of names.
        """
        results = results[0:6]
        if results[0][1] > 0.95:
            final_result = results[0][0]
            return final_result.name
        from collections import Counter

        # Extract names from the results
        names = [result[0].name for result in results if result]
        names.append(results[0][0].name)
        inputs = [result[2] for result in results if result]

        cell_value = results[0][3]

        number_present = re.search(r'\d+\.?\d*', cell_value)
        unit_present = (len(parser.parse(cell_value)) > 0)
        # Check specifically if both numbers and units are found

        if number_present:
            names =[*names, "Property", "Parameter"]
        if unit_present:
            names = [*names, "Property", "Parameter"]
            # Count each name's occurrence
        name_counts = Counter(names)
        # Find the most common name and the number of times it appears
        most_common_name, most_common_count = name_counts.most_common(1)[0]

        return most_common_name

    def create_data(self):
        """
        Method to check the format of the table data.
        This method should be implemented in subclasses.
        """
        try:
            # Reset the file pointer to the start of the file
            self.file.seek(0)

            # Read the CSV data into a DataFrame
            self._data = pd.read_csv(self.file, header=None)
            return True


        except Exception as e:
            return False







    def _process(self, **kwargs):
        """
        Transform the data.
        """
        if self._pre_check(index = kwargs['index'], element = kwargs['element']):
            return
        elif self._check_cache(index = kwargs['index'], element = kwargs['element']):
            return
        else:
            self._transform(index = kwargs['index'], element = kwargs['element'])

    def _create_input_string(self, index, element):
        first_non_null_value = element['column_values'][0]
        return f"\"{element['header']}\": \"{first_non_null_value}\""

    def _pre_check(self, index, element):
        """
        Perform a check before processing the data.
        """
        column = element['column_values']
        if len(column) == 0:
            return True
        return False

    def _update(self, result, input_string, **kwargs):
        """
        Update the classification result.
        """
        self._results.append({
            **kwargs['element'],
            "cached": False,
            "input_string": input_string.replace("\n", ""),
            "1_label": result,
        })
        ImporterCache.update(kwargs['element']['header'], column_label=result, attribute_type=self.attribute_type)

    def _llm_request(self, input_string, **kwargs):
        """
        Send a request to the node label model.
        """
        output = NodeLabel.nodes.get_by_string(string=input_string, limit=5,
                                               include_similarity=True, include_input_string=True)
        return output

    def _update_with_cache(self, cached, **kwargs):
        """
        Update the classification result with a cached result.
        """
        self._results.append(
            {
            **kwargs['element'],
            "cached": True,
            "input_string": None,
            "1_label": cached[1],
        })


    def _update_with_chat(self, result, input_string, **kwargs):
        """
        Update the classification result with a chat result.
        """
        self._results.append({
            **kwargs['element'],
            "cached": False,
            "input_string": input_string.replace("\n", ""),
            "1_label": result,
            **{f"{i}_label": None for i in range(2, 5)},
            **{f"{i}_sublabel": None for i in range(1, 5)},
            **{f"{i}_similarities": None for i in range(1, 5)}
        })
        ImporterCache.update(kwargs['element']['header'], column_label=result, attribute_type=self.attribute_type)

    def build_results(self):
        """
        Build the classification results.
        """
        self._results = sorted(self._results, key=lambda x: x['index'])







