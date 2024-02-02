import _io
import csv
import os

import django

from graphutils.general import TableDataTransformer
from importing.NodeLabelClassification.setupMessages import CLASSIFY_PROPERTY_PARAMETERS
from importing.utils.openai import chat_with_gpt4, chat_with_gpt3

django.setup()

from graphutils import config
from datetime import datetime
from quantulum3 import parser

from dotenv import load_dotenv

from dbcommunication.ai.createEmbeddings import request_embedding
from importing.models import LabelClassificationReport, NodeLabel, ImporterCache
import pandas as pd
import re

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

    def create_data(self):
        """
        Method to check the format of the table data.
        This method should be implemented in subclasses.
        """
        print("create data")
        try:
            # Reset the file pointer to the start of the file
            self.file.seek(0)

            # Read the CSV data into a DataFrame
            self._data = pd.read_csv(self.file, header=None)
            return True


        except Exception as e:
            print(f"Error: {e}")
            return False


    # def check_if_abbreviation(self, header):
    #     # Assuming 'kwargs' contains a dictionary with a key 'element',
    #     # and 'element' is a dictionary with a key 'header' which is a string.
    #
    #     # Regular Expression to match abbreviations
    #     abbreviation_pattern = re.compile(r'^[\w\d%°Ω()\/\-\+.\s]+(A/cm²|V|RH|C)?$', re.IGNORECASE)
    #
    #     # Check if the header matches the abbreviation pattern
    #     if abbreviation_pattern.match(header):
    #         return True
    #     else:
    #         return False

    def handle_units(self, index, element):
        """
        Handle units in the data.
        """
        query = (f"Context: \"{self.context}\".\n"
                 f"Header: of the \"{element['header']}\" \n"
                 f"""Rows: {", ".join(element['column_values'][:4])} \n""")
        print("Header:", element['header'])
        result = chat_with_gpt4(setup_message= CLASSIFY_PROPERTY_PARAMETERS, prompt = query)
        if result == "Parameter" or result == "Property":
            print(f"Updating with chat result {result}")
            self._update_with_chat(result = result, input_string = query, index = index, element = element)


    def _process(self, **kwargs):
        """
        Transform the data.
        """
        print(f"Processing {kwargs['element']['header']}...")
        print(f"Column values: {kwargs['element']['column_values'][0]}")
        if self._pre_check(index = kwargs['index'], element = kwargs['element']):
            return
        elif self._check_cache(index = kwargs['index'], element = kwargs['element']):
            return
        elif self.contains_units(kwargs['element']['header'] + str(kwargs['element']['column_values'][0])):
            self.handle_units(index = kwargs['index'], element = kwargs['element'])
        else:
            self._transform(index = kwargs['index'], element = kwargs['element'])

    def _create_input_string(self, index, element):
        first_non_null_value = element['column_values'][0]
        return f"Define the term \"{element['header']}\" (example: \"{first_non_null_value}\" is a \"{element['header']}\")..."

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
            **{f"{i+1}_label": r[0].name for i, r in enumerate(result)},
            **{f"{i+1}_sublabel": r[2] for i, r in enumerate(result)},
            **{f"{i+1}_similarity": r[1] for i, r in enumerate(result)}
        })
        ImporterCache.update(kwargs['element']['header'], column_label=result[0][0].name, attribute_type=self.attribute_type)

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
            **{f"{i}_label": None for i in range(2, 5)},
            **{f"{i}_sublabel": None for i in range(1, 5)},
            **{f"{i}_similarities": None for i in range(1, 5)}
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







