# Ensure the environment variable is set (replace 'myproject.settings' with your Django project's settings)
from langchain_core.runnables import RunnableParallel

from importing.LLMEvaluation.evaluation import LLMEvaluator, evaluate_JSONs, predict_nodes
from importing.NodeExtraction.nodeExtractor import aggregate_manufacturing, validate_manufacturings, aggregate_matters, \
    validate_matters, aggregate_parameters, validate_parameters, aggregate_measurement, validate_measurements, \
    aggregate_properties, validate_properties
from importing.NodeExtraction.nodeExtractor import build_results


class ManufacturingEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Manufacturing_Extraction",
                 experiment_prefix="manufacturing_evaluation", metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict_nodes,
                 chain=RunnableParallel(
                     manufacturingNodes=aggregate_manufacturing | validate_manufacturings) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))


class PropertyEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Property_Extraction",
                 experiment_prefix="property_evaluation", metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict_nodes,
                 chain=RunnableParallel(manufacturingNodes=aggregate_properties | validate_properties) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))


class ParameterEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Parameter_Extraction",
                 experiment_prefix="parameter_evaluation", metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict_nodes,
                 chain=RunnableParallel(manufacturingNodes=aggregate_parameters | validate_parameters) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))


class MeasurementEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Measurement_Extraction",
                 experiment_prefix="measurement_evaluation", metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict_nodes,
                 chain=RunnableParallel(
                     manufacturingNodes=aggregate_measurement | validate_measurements) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))


class MatterEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Matter_Extraction",
                 experiment_prefix="matter_evaluation",
                 metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict_nodes,
                 chain=RunnableParallel(matterNodes=aggregate_matters | validate_matters) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))


class MetadataEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Metadata_Extraction",
                 experiment_prefix="metadata_evaluation", metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict_nodes,
                 chain=RunnableParallel(
                     manufacturingNodes=aggregate_manufacturing | validate_manufacturings) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))


