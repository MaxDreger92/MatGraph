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
            print("Pre-check failed")
            return
        elif self._check_cache(index = kwargs['index'], element = kwargs['element']):
            return
        elif self.contains_units(kwargs['element']['header'] + str(kwargs['element']['column_values'][0])):
            print("Contains units")
            self.handle_units(index = kwargs['index'], element = kwargs['element'])
        # elif self.check_if_abbreviation(kwargs['element']['header']):
        #     return
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
            print("No column values", element['header'])
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
        print("NodeName", result[0][0].name)
        ImporterCache.update(kwargs['element']['header'], column_label=result[0][0].name, attribute_type=self.attribute_type)

    def _llm_request(self, input_string, **kwargs):
        """
        Send a request to the node label model.
        """
        print(f"Requesting classification for {input_string}")
        output = NodeLabel.nodes.get_by_string(string=input_string, limit=5,
                                               include_similarity=True, include_input_string=True)
        print(output[0][0].name)
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
        print("Chat result", result)
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





class ClassifierTester:
    """
    This class tests the classification results against actual labels and provides various utilities
    to assess and store the performance and results of the classification.
    """

    def __init__(self, predicted_labels, sample_csv_path):
        """
        Initialize the ClassifierTester with predicted labels and a path to the sample CSV file.

        Args:
            predicted_labels (list): A list of dictionaries containing predicted labels for each heading.
            sample_csv_path (str): The file path to the sample CSV.
        """
        self.predicted_labels = predicted_labels
        self.sample_csv_path = sample_csv_path
        self.actual_labels = self._get_actual_labels()

    def _get_actual_labels(self):
        """
        Private method to extract the actual labels from the specified row in the CSV file.

        Returns:
            Series: A pandas Series containing actual labels for each heading.
        """
        df = pd.read_csv(self.sample_csv_path)
        return df.iloc[69]  # assuming row 70 has the actual labels

    def validate_predictions(self):
        """
        Validate the predicted labels against the actual labels and calculate the accuracy.

        Returns:
            float: The accuracy of the predictions as a value between 0 and 1.
        """
        correct_predictions = sum(
            1 for predicted_label in self.predicted_labels
            if self.actual_labels[predicted_label["column_index"]] == predicted_label["predicted_labels"][0]
        )
        total_predictions = len(self.predicted_labels)
        accuracy = correct_predictions / total_predictions if total_predictions else 0
        print(accuracy, total_predictions)
        return accuracy

    def report_discrepancies(self):
        """
        Reports the discrepancies between the predicted labels and the actual labels.

        Returns:
            None
        """
        for predicted_label in self.predicted_labels:
            actual_label = self.actual_labels[predicted_label["column_index"]]
            prediction = predicted_label["predicted_labels"][0]
            if prediction != actual_label:
                print(f'Header: {predicted_label["header"]}, Predicted: {prediction}, Actual: {actual_label}, column: {predicted_label["column_index"]}' )

    def store_results_to_csv(self):
        """
        Stores the results of the classification comparison to a CSV file.

        Returns:
            None
        """
        filename = f"{datetime.now():%Y-%m-%d_%H-%M-%S}_{int(self.validate_predictions() * 100)}.csv"
        headers = ['Heading', 'Input', 'Ground Truth', 'Correct Prediction'] + \
                  [f'{i}. Predicted Label' for i in range(1, 6)] + \
                  [f'{i}. Predicted Sub-label' for i in range(1, 6)] + \
                  [f'{i}. Similarity' for i in range(1, 6)]

        with open(filename, 'w', newline='') as file:
            csv_writer = csv.DictWriter(file, fieldnames=headers)
            csv_writer.writeheader()

            for predicted_label_data in self.predicted_labels:
                actual_label = self.actual_labels[predicted_label_data["column_index"]]
                correct_prediction = actual_label == predicted_label_data["full_result"][0][0].name

                row = {
                    'Heading': predicted_label_data["header"],
                    'Input': predicted_label_data["input_string"],
                    'Ground Truth': actual_label,
                    'Correct Prediction': correct_prediction
                }

                # Unpack predictions into the row
                for i, result in enumerate(predicted_label_data["full_result"], start=1):
                    row[f'{i}. Predicted Label'] = result[0].name
                    row[f'{i}. Predicted Sub-label'] = result[2]
                    row[f'{i}. Similarity'] = result[1]

                csv_writer.writerow(row)

def count_lines_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return len(file.readlines())




def classify_and_test(sample_csv_path):
    """
    Classify the data and test the accuracy of the classifications.

    Args:
        sample_csv_path (str): The path to the sample CSV file.
    """
    df = pd.read_csv(sample_csv_path, header= None)
    print("Starting classification...")
    classifier = NodeClassifier(df, {"context": "Solar Cell Fabrication", 'file_link': "file_name", 'file_name': "file_name"})
    classifier.classify()
    print("Classification completed.")

    print("Testing classifier accuracy...")
    tester = ClassifierTester(classifier.predicted_labels, sample_csv_path)
    accuracy = tester.validate_predictions()
    print(f"Accuracy: {accuracy * 100:.2f}%")

    print("Reporting discrepancies between predicted and actual labels...")
    tester.report_discrepancies()

    print("Storing results to CSV...")
    tester.store_results_to_csv()
    print("Results stored successfully.")

    print("Predicted labels:")

def create_and_connect_node_embeddings(node_embedding_inputs, embedding_mapper, request_embedding):
    """
    Create NodeLabelEmbedding instances and connect them to their corresponding NodeLabel.

    Args:
        node_embedding_inputs (dict): A dictionary of inputs for embedding.
        embedding_mapper (dict): A dictionary mapping keys to NodeLabel names.
        request_embedding (func): A function that requests the embedding for a given input.

    Returns:
        list: A list of created and connected NodeLabelEmbedding instances.
    """
    nodes_created_and_connected = []

    for key, value in node_embedding_inputs.items():
        try:
            # Retrieve the corresponding NodeLabel
            node_label = NodeLabel.nodes.get(name=embedding_mapper[key])
            # Request the embedding vector for the input value
            vector = request_embedding(value)
            # Get or create the NodeLabelEmbedding instance
            node_embedding, created = NodeLabelEmbedding.get_or_create({'input': value, 'vector': vector})
            print(f"NodeLabelEmbedding {'created' if created else 'retrieved'}: {node_embedding}")

            # Connect the NodeLabelEmbedding instance to the NodeLabel
            rel = node_embedding.label.connect(node_label)
            print(f"Relationship {'created' if rel else 'exists'} between NodeLabelEmbedding and NodeLabel.")

            nodes_created_and_connected.append(node_embedding)

        except Exception as e:
            print(f"An error occurred while processing {key}: {e}")

    return nodes_created_and_connected

def setup_environment():
    """
    Set up the environment by loading environmental variables, configuring the database,
    and setting up Django.
    """
    print("Setting up the environment...")

    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    # Load environment variables from .env file
    load_dotenv()

    # Set default Django settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")

    # Configure NeoModel
    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
    print(f"Neo4j Database URL: {config.DATABASE_URL}")

    # Set up Django
    django.setup()

    print("Django environment set up successfully.")

if __name__ == "__main__":
    # Set up the environment before running any Django code
    setup_environment()

    sample_csv_path = "../../../data/materials.csv"

    # Now it's safe to import Django models
    from importing.models import NodeLabel, NodeLabelEmbedding, LabelClassificationReport

    # Run the classification and testing process
    classify_and_test(sample_csv_path)



