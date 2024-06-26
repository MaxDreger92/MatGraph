from multiprocessing import Pool

import numpy as np
from langchain.evaluation import load_evaluator
from langchain_core.runnables import Runnable
from langsmith import Client
from langsmith.evaluation import evaluate, run_evaluator
from langsmith.schemas import Run, Example
from scipy.optimize import linear_sum_assignment
from sklearn.metrics.pairwise import cosine_similarity

from graphutils.embeddings import request_embedding


def predict_nodes(chain) -> dict:
    def predict(inputs) -> dict:
        node_list = chain.invoke({
            'input': inputs['raw_data'],
            'context': inputs['context'],
            'first_line': inputs['first_line'],
            'header': inputs['header']
        })
        return node_list

    return predict


def predict_rels(chain) -> dict:
    def predict(inputs) -> dict:
        node_list = chain.invoke({
            'input': inputs['raw_data'],
            'context': inputs['context'],
            'first_line': inputs['first_line'],
            'header': inputs['header']
        })
        return node_list

    return predict


def canonicalize(data):
    """
    Recursively sort keys and canonicalize the JSON data.
    """
    if isinstance(data, dict):
        # Sort the dictionary by key
        return {k: canonicalize(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        # Recursively apply canonicalization to each item in the list
        return [canonicalize(item) for item in data]
    else:
        # Base case: return the data as is (numbers, strings, etc.)
        return data


def ensure_list(obj):
    if isinstance(obj, list):
        return obj
    else:
        return [obj]


@run_evaluator
def evaluate_JSONs(run: Run, example: Example) -> dict:
    prediction = run.outputs.get("output")
    required = example.outputs.get("nodes")
    prediction = [{key: value for key, value in d.items() if key != 'id' and key != 'label'} for d in prediction]
    required = [{key: value for key, value in d.items() if key != 'id' and key != 'label'} for d in required]
    canonicalized_prediction = str(canonicalize(prediction))
    canonicalized_required = str(canonicalize(required))

    evaluator = load_evaluator(
        "embedding_distance"
    )
    result = evaluator.evaluate_strings(prediction=canonicalized_prediction, reference=canonicalized_required)
    return {"key": "evaluate_output", "score": result['score']}



def attributes_to_key_value_pairs(attributes):
    key_value_pairs = {}
    for key, values in attributes.items():
        list_values = ensure_list(values)
        if key not in key_value_pairs:
            key_value_pairs[key] = []
        for value in list_values:
            key_value_pairs[key].append([value["value"], value["index"]])
    return key_value_pairs

def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def precompute_embeddings(attributes_list):
    unique_strings = set()
    for attributes in attributes_list:
        for key, values in attributes.items():
            for value in ensure_list(values):
                if not is_number(value["value"]) and value["value"] != "":
                    unique_strings.add(value["value"].lower())
                if not is_number(value["index"]):
                    unique_strings.add(value["index"].lower() and value["index"] != "")
    embeddings = {string: request_embedding(string) for string in unique_strings}
    return embeddings

def cosine_similarity_strings(str1, str2, embeddings):
    vector1 = embeddings[str1.lower()]
    vector2 = embeddings[str2.lower()]
    vec1 = np.array(vector1).reshape(1, -1)
    vec2 = np.array(vector2).reshape(1, -1)
    similarity = cosine_similarity(vec1, vec2)
    return similarity[0][0]

def hungarian(cost_matrix):
    cost_matrix = np.array(cost_matrix)
    cost_matrix = cost_matrix * -1
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    total_cost = cost_matrix[row_ind, col_ind].sum() * -1
    num_pairs = len(row_ind)
    normalized_cost = total_cost / num_pairs
    return normalized_cost

def compute_similarity(pair, embeddings):
    (values_o_list, values_g_list), (o_idx, g_idx) = pair
    value_o, index_o = values_o_list[o_idx]
    value_g, index_g = values_g_list[g_idx]
    if value_o is None and value_g is None:
        return 1 if index_o == index_g else 0.5
    if is_number(value_o) and is_number(value_g):
        if float(value_o) == float(value_g):
            return 1 if index_o == index_g else 0.5
        else:
            return 0.5 if index_o == index_g else 0
    if is_number(value_o) or is_number(value_g):
        return 0
    if isinstance(value_o, str) and isinstance(value_g, str):
        if value_o.lower() == value_g.lower():
            return 1 if index_o == index_g else 0.5
        elif value_o == "" or value_g == "":
            return 0
        else:
            similarity = cosine_similarity_strings(value_o, value_g, embeddings)
            return similarity if index_o == index_g else similarity * 0.5

def calculate_similarity_matrix(args):
    try:
        prediction, required, p_idx, r_idx, embeddings = args
        node_o = prediction[p_idx]
        node_g = required[r_idx]
        values_o = attributes_to_key_value_pairs(node_o["attributes"])
        values_g = attributes_to_key_value_pairs(node_g["attributes"])
        keys_o = set(values_o.keys())
        keys_g = set(values_g.keys())
        intersection = keys_o & keys_g
        union = keys_o | keys_g
        scores = []
        for key in intersection:
            values_o_list = values_o[key]
            values_g_list = values_g[key]
            len_o = len(values_o_list)
            len_g = len(values_g_list)
            pairs = [((values_o_list, values_g_list), (i, j)) for i in range(len_o) for j in range(len_g)]
            inner_matrix = [compute_similarity(pair, embeddings) for pair in pairs]
            inner_matrix = np.array(inner_matrix).reshape(len_o, len_g)
            scores.append(hungarian(inner_matrix))
        if scores:
            return sum(scores) / len(union)
        return 0
    except Exception as e:
        print(f"Error in calculate_similarity_matrix: {e}")
        return 0

@run_evaluator
def evaluate_nodes(run, example):
    try:
        prediction = run.outputs.get("output")
        required = example.outputs.get("nodes")
        attributes_list = [node["attributes"] for node in prediction + required]
        embeddings = precompute_embeddings(attributes_list)
        len_p = len(prediction)
        len_r = len(required)
        args = [(prediction, required, p_idx, r_idx, embeddings) for p_idx in range(len_p) for r_idx in range(len_r)]
        with Pool() as pool:
            similarity_matrix = pool.map(calculate_similarity_matrix, args)
        similarity_matrix = np.array(similarity_matrix).reshape(len_p, len_r)
        result = hungarian(similarity_matrix)
        return {"key": "evaluate_nodes", "score": result}
    except Exception as e:
        return {"key": "evaluate_nodes", "score": 0}


@run_evaluator
def evaluate_rels_f1(run, example):
    """Calculate precision, recall, and F1 score based on the overlap of connections between the output and reference."""

    # Helper function to sort lists of dictionaries by connection tuples
    def sorted_connections(connections):
        return sorted(connections, key=lambda x: (x['connection'], x['rel_type']))

    # Retrieve and sort output and reference connections
    output_list = sorted_connections(run.outputs.get("output", []))
    reference_list = sorted_connections(example.outputs.get("output", []))
    # Convert sorted lists of connections to sets of tuples for comparison
    output = set((d['rel_type'], tuple(d['connection'])) for d in output_list)
    reference = set((d['rel_type'], tuple(d['connection'])) for d in reference_list)

    # Determine True Positives (TP), False Positives (FP), and False Negatives (FN)
    true_positives = output.intersection(reference)
    false_positives = output.difference(reference)
    false_negatives = reference.difference(output)
    # Calculate precision and recall
    precision = len(true_positives) / (len(true_positives) + len(false_positives)) if output else 0
    recall = len(true_positives) / (len(true_positives) + len(false_negatives)) if reference else 0
    # Calculate F1 score
    if precision + recall == 0:  # Avoid division by zero if both precision and recall are zero
        f1_score = 0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)
    return {"key": "f1", "score": f1_score, "precision": precision, "recall": recall}

@run_evaluator
def evaluate_rels_recall(run, example):
    """Calculate precision, recall, and F1 score based on the overlap of connections between the output and reference."""

    # Helper function to sort lists of dictionaries by connection tuples
    def sorted_connections(connections):
        return sorted(connections, key=lambda x: (x['connection'], x['rel_type']))

    # Retrieve and sort output and reference connections
    output_list = sorted_connections(run.outputs.get("output", []))
    reference_list = sorted_connections(example.outputs.get("output", []))
    # Convert sorted lists of connections to sets of tuples for comparison
    output = set((d['rel_type'], tuple(d['connection'])) for d in output_list)
    reference = set((d['rel_type'], tuple(d['connection'])) for d in reference_list)

    # Determine True Positives (TP), False Positives (FP), and False Negatives (FN)
    true_positives = output.intersection(reference)
    false_positives = output.difference(reference)
    false_negatives = reference.difference(output)
    # Calculate precision and recall
    precision = len(true_positives) / (len(true_positives) + len(false_positives)) if output else 0
    recall = len(true_positives) / (len(true_positives) + len(false_negatives)) if reference else 0
    # Calculate F1 score
    if precision + recall == 0:  # Avoid division by zero if both precision and recall are zero
        f1_score = 0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)
    return {"key": "recall", "score": recall, "precision": precision, "recall": recall}

@run_evaluator
def evaluate_rels_precision(run, example):
    """Calculate precision, recall, and F1 score based on the overlap of connections between the output and reference."""

    # Helper function to sort lists of dictionaries by connection tuples
    def sorted_connections(connections):
        return sorted(connections, key=lambda x: (x['connection'], x['rel_type']))

    # Retrieve and sort output and reference connections
    output_list = sorted_connections(run.outputs.get("output", []))
    reference_list = sorted_connections(example.outputs.get("output", []))
    # Convert sorted lists of connections to sets of tuples for comparison
    output = set((d['rel_type'], tuple(d['connection'])) for d in output_list)
    reference = set((d['rel_type'], tuple(d['connection'])) for d in reference_list)

    # Determine True Positives (TP), False Positives (FP), and False Negatives (FN)
    true_positives = output.intersection(reference)
    false_positives = output.difference(reference)
    false_negatives = reference.difference(output)
    # Calculate precision and recall
    precision = len(true_positives) / (len(true_positives) + len(false_positives)) if output else 0
    recall = len(true_positives) / (len(true_positives) + len(false_negatives)) if reference else 0
    # Calculate F1 score
    if precision + recall == 0:  # Avoid division by zero if both precision and recall are zero
        f1_score = 0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)
    return {"key": "precision", "score": precision, "precision": precision, "recall": recall}

class LLMEvaluator:
    def __init__(self, data_set, experiment_prefix, metadata, chain: Runnable, evaluators, predict_function):
        self.client = Client()
        self.data_set = data_set
        self.experiment_prefix = experiment_prefix
        self.metadata = metadata
        self.chain = chain
        self.evaluators = evaluators
        self.predict_function = predict_function

    def add_evaluator(self, evaluator):
        """Adds an evaluator function to the list of evaluators."""
        self.evaluators.append(evaluator)

    def run_evaluation(self):
        """Runs the evaluation by applying the predict function to the data and applying each evaluator."""
        # Simulate loading data and running predictions; you'd replace this with your actual data handling and model inference logic.
        experiment_results = evaluate(
            self.predict_function,  # Your AI system
            data=self.data_set,  # The data to predict and grade over
            evaluators=self.evaluators,  # The evaluators to score the results
            experiment_prefix=self.experiment_prefix,  # A prefix for your experiment names to easily identify them
            metadata={
                "version": "1.0.0",
            },
        )
        print("Experiment results", experiment_results)
