import os
import django



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mat2devplatform.settings')
# Set up Django
django.setup()

from importing.LLMEvaluation.RelationshipEvaluators import HasParameterEvaluator, HasPropertyEvaluator, \
    HasManufacturingEvaluator, HasMeasurementEvaluator

from importing.LLMEvaluation.NodeEvaluators import ManufacturingEvaluator, MatterEvaluator, PropertyEvaluator, \
    ParameterEvaluator, MeasurementEvaluator, MetadataEvaluator

# Example usage
if __name__ == "__main__":
    # Assuming a function 'predict' and a 'data' structure already exist
    # manufacturing_data_set = "Manufacturing_Extraction"
    # manufacturing_evaluation = ManufacturingEvaluator()
    # manufacturing_results = manufacturing_evaluation.run_evaluation()
    #
    # matter_data_set = "Matter_Extraction"
    # matter_evaluation = MatterEvaluator()
    # matter_results = matter_evaluation.run_evaluation()
    # #
    # property_data_set = "Property_Extraction"
    # property_evaluation = PropertyEvaluator()
    # property_results = property_evaluation.run_evaluation()
    #
    # parameter_data_set = "Parameter_Extraction"
    # parameter_evaluation = ParameterEvaluator()
    # parameter_results = parameter_evaluation.run_evaluation()
    # #
    # measurement_data_set = "Measurement_Extraction"
    # measurement_evaluation = MeasurementEvaluator()
    # measurement_results = measurement_evaluation.run_evaluation()
    #
    # metadata_data_set = "Metadata_Extraction"
    # metadata_evaluation = MetadataEvaluator()
    # metadata_results = metadata_evaluation.run_evaluation()
    #
    # has_parameter_data_set = "Has_Parameter_Extraction"
    # has_parameter_evaluation = HasParameterEvaluator()
    # has_parameter_results = has_parameter_evaluation.run_evaluation()
    #
    # has_property_data_set = "Has_Property_Extraction"
    # has_property_evaluation = HasPropertyEvaluator()
    # has_property_results = has_property_evaluation.run_evaluation()

    # has_manufacturing_data_set = "Has_Manufacturing_Extraction"
    # has_manufacturing = HasManufacturingEvaluator()
    # has_manufacturing_results = has_manufacturing.run_evaluation()

    has_measurement_data_set = "Has_Measurement_Extraction"
    has_measurement = HasMeasurementEvaluator()
    has_measurement_results = has_measurement.run_evaluation()

    has_part_matter_data_set = "Has_Part_Matter_Extraction"
    has_part_matter = HasPartMatterEvaluator()
    has_part_matter_results = has_part_matter.run_evaluation()

    # has_metadata_data_set = "Has_Metadata_Extraction"
    # has_metadata = HasMetadataEvaluator()
    # has_metadata_results = has_metadata.run_evaluation()



