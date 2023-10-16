import csv
import pickle
from datetime import datetime

from config import node_embedding_inputs, embedding_mapper
from src.utils.config import EMBEDDING_DIMENSIONS
from src.utils.data_processing import get_unique_csv_headers, get_true_node_label, get_first_cell_for_heading
from src.utils.openai import request_embedding


class EmbeddingSearch:

    def __init__(self):

        self.embeddings = []
        self.node_labels = []
        self.input_strings = []

    def generate_embeddings(self, node_labels):
        # import here to avoid loading faiss for everything django does
        import faiss
        import numpy as np
        self.node_labels = node_labels
        for label in node_labels:
            self.embeddings.append(request_embedding(node_labels[label]))

        # Create FAISS index
        self.index = faiss.IndexFlatIP(EMBEDDING_DIMENSIONS)
        self.index.add(np.array([
            np.array(row) for row in self.embeddings
        ]))

    def store_data_to_file(self, filename):
        """
        Store embeddings, input strings, and labels to a file using pickle.

        Parameters:
        - embeddings (list): A list of embeddings.
        - input_strings (list): A list of input strings.
        - labels (list): A list of labels.
        - filename (str): The name of the file where data will be stored.

        Returns:
        - None
        """

        data = {
            "embeddings": self.embeddings,
            "input_strings": list(self.node_labels.values()),
            "labels": list(self.node_labels.keys())
        }

        with open(filename, 'wb') as file:
            pickle.dump(data, file)

    def load_embeddings_from_file(self, filename):
        """
        Load embeddings, input strings, and labels from a file using pickle.

        Parameters:
        - filename (str): The name of the file from which data will be loaded.

        Returns:
        - dict: A dictionary containing embeddings, input strings, and labels.
        """
        import faiss
        import numpy as np

        with open(filename, 'rb') as file:
            data = pickle.load(file)
        self.node_labels = data["labels"]
        self.embeddings = data["embeddings"]
        self.input_strings = data["input_strings"]
        # Create FAISS index
        self.index = faiss.IndexFlatIP(EMBEDDING_DIMENSIONS)
        self.index.add(np.array([
            np.array(row) for row in self.embeddings
        ]))

    def find_vector(self, vector, n=5, include_similarities=False):
        """
        Find the closest embeddings in the index to the input vector.

        Args:
            vector (np.array): The input vector to find the closest embeddings for.
            n (int): The number of closest embeddings to return.
            include_similarities (bool): Whether to include similarities in the output.

        Returns: If `include_similarities` is False, returns a list of ids or a single id (if n=1). If
        `include_similarities` is True, returns a list of tuples (id, similarity) or a tuple (id, similarity) if n=1.
        """

        import numpy as np

        D, I = self.index.search(np.array([vector]), n)
        ids = [self.node_labels[i] for i in I[0]]

        if include_similarities:
            return ids[0], D[0][0] if n == 1 else [(ids[i], D[0][i]) for i in range(len(ids))]

        return ids[0] if n == 1 else ids

    def find_string(self, query, include_similarity=False, **kwargs):
        """
        Find the closest embeddings in the index to the input query.

        Args:
            query (str): The input string to find the closest embeddings for.
            include_similarity (bool): Whether to include similarities in the output.
            **kwargs: Additional keyword arguments to pass to the `find_vector` method.

        Returns:
            Depending on the input arguments, returns:
            - An instance of the model or an id
            - A list of tuples (model instance, similarity) or a list of tuples (id, similarity)
        """

        if not query:
            return (None, 0) if include_similarity else None
        res = self.find_vector(request_embedding(query), include_similarities=include_similarity, **kwargs)

        return res


class NodeClassifier:
    def __init__(self, sample_csv_path, embedding_search, embedding_mapper, new_node_label_embeddings=False,
                 embeddings_path='data.pkl'):
        """
        Initialize the NodeClassifier.

        :param sample_csv_path: Path to the CSV file containing samples.
        :param embedding_search: An instance of EmbeddingSearch class.
        :param embedding_mapper: A dictionary mapping embeddings to their corresponding labels.
        :param new_node_label_embeddings: A flag to indicate if new embeddings should be generated. Default is False.
        :param embeddings_path: Path to the stored embeddings file. Default is 'data.pkl'.
        """
        self.sample_csv_path = sample_csv_path
        self.es = embedding_search
        self.embedding_mapper = embedding_mapper

        if new_node_label_embeddings:
            # Assuming the correct method name is 'generate_embeddings' for embedding_search
            self.es.generate_embeddings(node_embedding_inputs)
            self.es.store_embeddings(embeddings_path)
        else:
            self.es.load_embeddings_from_file(embeddings_path)

        self._predicted_labels = {}

    def classify(self):
        """
        Classify the headings from the CSV file.

        Predicts labels for each heading and stores them in the predicted_labels dictionary.
        """
        headings = get_unique_csv_headers(self.sample_csv_path)

        for header in headings:
            element = get_first_cell_for_heading(self.sample_csv_path, header)
            if element == "" or str(element) == 'nan':
                element = ""
            else:
                element = "value: " + str(element)

            input_string = f"""key: {header} {element}"""
            query_result = self.es.find_string(input_string, include_similarity=True)
            input_string = input_string.replace("\n", "")

            # Store the predicted label in the dictionary
            self._predicted_labels[header] = input_string, query_result

    @property
    def predicted_labels(self):
        """Return the dictionary containing the predicted labels for each heading."""
        return self._predicted_labels


class ClassifierTester:
    def __init__(self, predicted_labels, sample_csv_path):
        """
        Initialize the ClassifierTester.

        :param predicted_labels: Dictionary containing predicted labels for each heading.
        :param sample_csv_path: Path to the CSV file containing samples.
        """
        self.predicted_labels = predicted_labels
        self.sample_csv_path = sample_csv_path
        self.actual_labels = self._get_actual_labels()

    def _get_actual_labels(self):
        """
        Extract the actual labels from the CSV file.

        :return: Dictionary containing actual labels for each heading.
        """
        actual_labels = {}
        headings = get_unique_csv_headers(self.sample_csv_path)
        for header in headings:
            actual_labels[header] = get_true_node_label(self.sample_csv_path, header)
        return actual_labels

    def validate_predictions(self):
        """
        Compare predicted labels with actual labels and calculate accuracy.

        :return: Accuracy of the predicted labels.
        """
        correct_predictions = 0
        total_predictions = len(self.predicted_labels)

        for header, predicted_label in self.predicted_labels.items():
            actual_label = self.actual_labels.get(header)
            if actual_label and embedding_mapper[predicted_label[1][0]] == actual_label:
                correct_predictions += 1

        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        print(accuracy, total_predictions)
        return accuracy

    def report_discrepancies(self):
        """
        Print a report of the discrepancies between predicted and actual labels.

        :return: None
        """
        for header, predicted_label in self.predicted_labels.items():
            actual_label = self.actual_labels.get(header)
            prediction = embedding_mapper[predicted_label[1][0]]
            if prediction != actual_label:
                print(f"Header: {header}, Predicted: {prediction}, Actual: {actual_label}")

    def store_results_to_csv(self):
        """
        Store the comparison results in a CSV file.

        :return: None
        """
        filename = f"{str(datetime.now())}_{str(int(self.validate_predictions() * 100))}.csv"

        headers = [
            'Heading', 'Input', 'Ground Truth', 'Correct Prediction',
            '1. Predicted Label', '2. Predicted Label', '3. Predicted Label', '4. Predicted Label',
            '1. Predicted Sub-label', '2. Predicted Sub-label', '3. Predicted Sub-label', '4. Predicted Sub-label',
            '1. Similarity', '2. Similarity', '3. Similarity', '4. Similarity'
        ]
        with open(filename, 'w', newline='') as file:
            csv_writer = csv.DictWriter(file, fieldnames=headers)
            csv_writer.writeheader()

            def get_predicted_label(predicted_label_data, idx):
                return embedding_mapper[predicted_label_data[1][1][idx][0]]

            def get_predicted_sub_label(predicted_label_data, idx):
                return predicted_label_data[1][1][idx][0]

            def get_similarity(predicted_label_data, idx):
                return predicted_label_data[1][1][idx][1]

            for header, predicted_label_data in self.predicted_labels.items():
                actual_label = self.actual_labels.get(header)

                row = {
                    'Heading': header,
                    'Input': predicted_label_data[0],
                    'Ground Truth': actual_label,
                    'Correct Prediction': actual_label == get_predicted_label(predicted_label_data, 0),
                    **{f'{i+1}. Predicted Label': get_predicted_label(predicted_label_data, i) for i in range(4)},
                    **{f'{i+1}. Predicted Sub-label': get_predicted_sub_label(predicted_label_data, i) for i in range(4)},
                    **{f'{i+1}. Similarity': get_similarity(predicted_label_data, i) for i in range(4)}
                }
                csv_writer.writerow(row)


if __name__ == "__main__":
    # Instantiate the EmbeddingSearch class
    embeddings_search = EmbeddingSearch()  # Assuming EmbeddingSearch is defined elsewhere
    sample_csv_path = "../../data/materials.csv"

    classifier = NodeClassifier(sample_csv_path, embeddings_search, embedding_mapper)
    classifier.classify()

    tester = ClassifierTester(classifier.predicted_labels, sample_csv_path)
    accuracy = tester.validate_predictions()
    print(f"Accuracy: {accuracy * 100:.2f}%")

    print("\nDiscrepancies:")
    tester.report_discrepancies()
    tester.store_results_to_csv()
