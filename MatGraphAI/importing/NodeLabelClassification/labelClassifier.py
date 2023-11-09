import csv
import os
import django
django.setup()

from graphutils import config
from datetime import datetime

from dotenv import load_dotenv

from dbcommunication.ai.createEmbeddings import request_embedding

from importing.models import NodeLabel, NodeLabelEmbedding








import pandas as pd

class NodeClassifier:
    """
    A classifier that processes a CSV file, extracts headers and classifies them using a node label model.
    """

    def __init__(self, sample_csv_path):
        """
        Initialize the NodeClassifier with the path to a CSV file.

        Args:
            sample_csv_path (str): The file path to the sample CSV.
        """
        self.sample_csv_path = sample_csv_path
        self._predicted_labels = []

    def classify(self):
        """
        Classify the headers in the CSV file. Predicts labels for each header and stores the results.
        """
        # Read the CSV file, skipping the header as we will process it separately
        df = pd.read_csv(self.sample_csv_path, header=None)
        headers = df.iloc[0]
        df = pd.read_csv(self.sample_csv_path)

        for column_index, header in enumerate(headers):
            # Select the column by header after skipping the first row (header row)
            column = df[header]

            # Skip if column is empty (excluding the header)
            if column.isnull().all():
                print(f"Skipping column: {header}")
                continue

            # Find the first non-null value in the column
            first_non_null_value = column.dropna().iloc[0]

            input_string = (f"Define the term \"{header}\" (example: \"{first_non_null_value}\" "
                            f"is a \"{header}\") in a three word sentence, on a very high abstraction-level"
                            f"(matter, manufacturing, measurement, property, parameter, equipment, laboratory)!")

            # Assuming NodeLabel is a defined class with a method 'get_by_string' used for classification
            query_result = NodeLabel.nodes.get_by_string(string=input_string, limit=4,
                                                         include_similarity=True, include_input_string=True)

            # Store the predicted label in the list
            self._predicted_labels.append({
                "header": header,
                "column_index": column_index,
                "pd_header": header,  # The key 'pd_header' seems redundant since it's the same as 'header'
                "input_string": input_string.replace("\n", ""),
                "predicted_label": query_result[0][0].name,
                "predicted_sublabel": query_result[0][2],
                "full_result": query_result
            })

    @property
    def predicted_labels(self):
        """
        Gets the predicted labels after classification has been run.

        Returns:
            list: A list of dictionaries containing the predicted labels and related information.
        """
        return self._predicted_labels


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
            if self.actual_labels.get(predicted_label["pd_header"]) == predicted_label["predicted_label"]
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
            actual_label = self.actual_labels.get(predicted_label["pd_header"])
            prediction = predicted_label["predicted_label"]
            if prediction != actual_label:
                print(f'Header: {predicted_label["header"]}, Predicted: {prediction}, Actual: {actual_label}')

    def store_results_to_csv(self):
        """
        Stores the results of the classification comparison to a CSV file.

        Returns:
            None
        """
        filename = f"{datetime.now():%Y-%m-%d_%H-%M-%S}_{int(self.validate_predictions() * 100)}.csv"
        headers = ['Heading', 'Input', 'Ground Truth', 'Correct Prediction'] + \
                  [f'{i}. Predicted Label' for i in range(1, 5)] + \
                  [f'{i}. Predicted Sub-label' for i in range(1, 5)] + \
                  [f'{i}. Similarity' for i in range(1, 5)]

        with open(filename, 'w', newline='') as file:
            csv_writer = csv.DictWriter(file, fieldnames=headers)
            csv_writer.writeheader()

            for predicted_label_data in self.predicted_labels:
                actual_label = self.actual_labels.get(predicted_label_data["pd_header"])
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
    print("Starting classification...")
    classifier = NodeClassifier(sample_csv_path)
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
    print(classifier.predicted_labels)

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
    from importing.models import NodeLabel, NodeLabelEmbedding

    # Run the classification and testing process
    classify_and_test(sample_csv_path)



