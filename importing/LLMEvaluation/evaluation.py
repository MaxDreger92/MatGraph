from langchain.evaluation import JsonEditDistanceEvaluator
from langchain_core.runnables import RunnableParallel, Runnable
from langsmith import Client
from langsmith.schemas import Run, Example

from langsmith.evaluation import evaluate

from importing.NodeExtraction.nodeExtractor import aggregate_manufacturing, validate_manufacturings
from importing.NodeExtraction.nodeExtractor import build_results

def predict(chain) -> dict:
    def predict(inputs) -> dict:
        node_list = chain.invoke({
            'input': inputs['raw_data'],
            'context': inputs['context'],
            'first_line': inputs['first_line'],
            'header': inputs['header']
        })
        return node_list
    return predict

def evaluate_JSONs(run: Run, example: Example) -> dict:
    prediction = run.outputs
    required = example.outputs
    prediction = [{key: value for key, value in d.items() if key != 'id'} for d in prediction]
    required = [{key: value for key, value in d.items() if key != 'id'} for d in required]

    evaluator = JsonEditDistanceEvaluator()
    print("Prediction", prediction)
    print("Required", required)
    result = evaluator.evaluate_strings(prediction=str(prediction).replace("'",'"'), reference=str(required).replace("'",'"'))
    return {"key":"evaluate_output", "score": result["score"]}

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


