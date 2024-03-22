import json

import django

from importing.RelationshipExtraction.input_generator import flatten_json, remove_key, extract_data

django.setup()

from langchain_core.runnables import chain, RunnableParallel

from importing.RelationshipExtraction.hasManufacturingExtractor import hasManufacturingExtractor
from importing.RelationshipExtraction.hasMeasurementExtractor import hasMeasurementExtractor
from importing.RelationshipExtraction.hasParameterExtractor import hasParameterExtractor
from importing.RelationshipExtraction.hasPropertyExtractor import hasPropertyExtractor
from importing.RelationshipExtraction.setupMessages import MANUFACTURING_PARAMETER_MESSAGE, \
    MATTER_MANUFACTURING_MESSAGE, PROPERTY_MEASUREMENT_MESSAGE, MATTER_PROPERTY_MESSAGE


def prepare_lists(json_input, label1, label2):
    label_one_data = [flatten_json(remove_key(extract_data(json_input, label), "position")) for label in label1]
    label_two_data = [flatten_json(remove_key(extract_data(json_input, label), "position")) for label in label2]

    label_two_data = [item for sublist in label_two_data for item in sublist]
    label_one_data = [item for sublist in label_one_data for item in sublist]

    return label_one_data, label_two_data
def extract_relationhsips(data, setup_message, label_one, label_two, extractor):
    list_1, list2 = prepare_lists(data, label_one, label_two)
    if len(list_1) > 0 or len(list2) > 0:
        return
    rel_extractor = extractor(data, setup_message, label_one, label_two, data['context'])
    return rel_extractor.initial_extraction()


@chain
def extract_has_property(data):
    property_extractor = hasPropertyExtractor(data['input'], MATTER_PROPERTY_MESSAGE, ["matter"], ["property"], data['context'])
    return property_extractor.initial_extraction()


@chain
def extract_has_measurement(data):
    measurement_extractor = hasMeasurementExtractor(data['input'], PROPERTY_MEASUREMENT_MESSAGE, ["measurement"], ["property"], data['context'])
    return measurement_extractor.initial_extraction()

@chain
def extract_has_manufacturing(data):
    manufacturing_extractor = hasManufacturingExtractor(data['input'], MATTER_MANUFACTURING_MESSAGE, ["matter"], ["manufacturing"], data['context'])
    return manufacturing_extractor.initial_extraction()

@chain
def extract_has_parameter(data):
    parameter_extractor = hasParameterExtractor(data['input'], MANUFACTURING_PARAMETER_MESSAGE, ["manufacturing", "measurement"], ["parameter"], data['context'])
    return parameter_extractor.initial_extraction()






@chain
def validate_has_property(extractor):
    print("validate_has_property")
    print(extractor)
    if extractor:
        return extractor.intermediate
    return


@chain
def validate_has_measurement(extractor):
    print("validate_has_measurement")
    print(extractor)
    if extractor:
        return extractor.intermediate
    return


@chain
def validate_has_manufacturing(extractor):
    print("validate_has_manufacturing")
    print(extractor)
    if extractor:
        return extractor.intermediate
    return


@chain
def validate_has_parameter(extractor):
    print("validate_has_parameter")
    print(extractor)
    if extractor:
        return extractor.intermediate
    return




@chain
def build_results(data):
    relationships = []
    for key, value in data.items():
        for item in value.relationships:
            relationships.append(
                {
                    'rel_type': item.type,
                    'connection': [str(item.source), str(item.target)]
                }
            )
    return relationships

class fullRelationshipsExtractor:
    def __init__(self, input_json, context):
        self._data = json.loads(input_json)
        self._context = context

    @property
    def data(self):
        return self._data

    @property
    def context(self):
        return self._context


    def run(self):
        # Ensure extractors are created
        # self.create_extractors()
        chain = RunnableParallel(
            has_property=extract_has_property | validate_has_property,
            has_measurement=extract_has_measurement | validate_has_measurement,
            has_manufacturing=extract_has_manufacturing | validate_has_manufacturing,
            has_parameter=extract_has_parameter | validate_has_parameter
        ) | build_results
        chain = chain.with_config({"run_name": "relationship-extraction"})
        self.relationships = chain.invoke({
            'input': self.data,
            'context': self.context,
        })


    @property
    def relationships(self):
        return self._relationships

    @relationships.setter
    def relationships(self, value):
        self._relationships = value

    @property
    def results(self):
        return {"nodes": self.data["nodes"], "relationships": self.relationships}


