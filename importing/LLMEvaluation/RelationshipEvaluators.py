from langchain_core.runnables import RunnableParallel

from importing.LLMEvaluation.evaluation import LLMEvaluator, evaluate_JSONs, predict
from importing.RelationshipExtraction.completeRelExtractor import build_results, extract_has_parameter, \
    validate_has_parameter, extract_has_property, validate_has_property, extract_has_manufacturing, \
    validate_has_manufacturing, extract_has_measurement, validate_has_measurement, extract_has_metadata, \
    validate_has_metadata


class HasParameterEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Has_Parameter_Extraction",
                 experiment_prefix="has_parameter_evaluation", metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict,
                 chain=RunnableParallel(hasParameterRels=extract_has_parameter | validate_has_parameter) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))


class HasPropertyEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Has_Property_Extraction",
                 experiment_prefix="has_property_evaluation", metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict,
                 chain=RunnableParallel(hasPropertyRels=extract_has_property | validate_has_property) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))


class HasManufacturingEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Has_Manufacturing_Extraction",
                 experiment_prefix="has_manufacturing_evaluation", metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict,
                 chain=RunnableParallel(hasManufacturingRels=extract_has_manufacturing | validate_has_manufacturing) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))

class HasMeasurementEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Has_Measurement_Extraction",
                 experiment_prefix="has_measurement_evaluation", metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict,
                 chain=RunnableParallel(hasMeasurementRels=extract_has_measurement | validate_has_measurement) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))

class HasMetadataEvaluator(LLMEvaluator):
    def __init__(self,
                 data_set="Has_Metadata_Extraction",
                 experiment_prefix="has_metadata_evaluation", metadata='',
                 evaluators=[evaluate_JSONs],
                 predict_function=predict,
                 chain=RunnableParallel(hasMetadataRels=extract_has_metadata | validate_has_metadata) | build_results,
                 ):
        super().__init__(data_set, experiment_prefix, metadata, chain, evaluators, predict_function(chain))
