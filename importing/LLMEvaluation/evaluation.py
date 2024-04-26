from langchain.evaluation import JsonEditDistanceEvaluator
from langchain_core.runnables import RunnableParallel, Runnable
from langsmith import Client
from langsmith.schemas import Run, Example

from langsmith.evaluation import evaluate, run_evaluator


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

@run_evaluator
def evaluate_JSONs(run: Run, example: Example) -> dict:
    print("Evaluating JSONs")
    prediction = run.outputs.get("output")
    required = example.outputs.get("output")
    prediction = [{key: value for key, value in d.items() if key != 'id'} for d in prediction]
    required = [{key: value for key, value in d.items() if key != 'id'} for d in required]
    print(prediction)
    print(required)

    evaluator = JsonEditDistanceEvaluator()
    print("Prediction", prediction)
    print("Required", required)
    result = evaluator.evaluate_strings(prediction=str(prediction).replace("'",'"'), reference=str(required).replace("'",'"'))
    return {"key":"evaluate_output", "score": result["score"]}

@run_evaluator
def evaluate_rels(run, example):
    """Calculate precision, recall, and F1 score based on the overlap of connections between the output and reference."""
    print("Evaluating relationships")
    print(run.outputs.get("output", []))
    print(example.outputs.get("output", []))

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
    print("True positives", true_positives)
    # Calculate precision and recall
    precision = len(true_positives) / (len(true_positives) + len(false_positives)) if output else 0
    recall = len(true_positives) / (len(true_positives) + len(false_negatives)) if reference else 0
    # Calculate F1 score
    if precision + recall == 0:  # Avoid division by zero if both precision and recall are zero
        f1_score = 0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)
    return {"key":"evaluate_rels", "score": f1_score, "comment": f"Precision: {precision}, Recall: {recall}"}


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
            self.predict_function, # Your AI system
            data=self.data_set, # The data to predict and grade over
            evaluators=self.evaluators, # The evaluators to score the results
            experiment_prefix=self.experiment_prefix, # A prefix for your experiment names to easily identify them
            metadata={
                "version": "1.0.0",
            },
        )
        print("Experiment results", experiment_results)


