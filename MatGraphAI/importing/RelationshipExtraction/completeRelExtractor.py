import json

import django
from langchain_core.prompts import FewShotPromptTemplate

from importing.RelationshipExtraction.input_generator import flatten_json, remove_key, extract_data
from importing.RelationshipExtraction.relationshipCorrector import hasParameterCorrector, hasPropertyCorrector, \
    hasManufacturingCorrector, hasMeasurementCorrector

django.setup()

from langchain_core.runnables import chain, RunnableParallel

from importing.RelationshipExtraction.hasManufacturingExtractor import hasManufacturingExtractor
from importing.RelationshipExtraction.hasMeasurementExtractor import hasMeasurementExtractor
from importing.RelationshipExtraction.hasParameterExtractor import hasParameterExtractor
from importing.RelationshipExtraction.hasPropertyExtractor import hasPropertyExtractor




def extract_relationships(input_json, context, extractor_type):
    extractor = extractor_type(input_json, context)
    if len(extractor.label_one_nodes) != 0  and len(extractor.label_two_nodes) != 0 :
        extractor.run()
        print('extractor', extractor.results)
        return extractor.results
    return None

@chain
def extract_has_property(data):
    print("extract has_property relationships")
    return extract_relationships(data['input'], data['context'], hasPropertyExtractor)


@chain
def extract_has_measurement(data):
    print("extract has_measurement relationships")
    return extract_relationships(data['input'], data['context'], hasMeasurementExtractor)

@chain
def extract_has_manufacturing(data):
    print("extract has_manufacturing relationships")
    return extract_relationships(data['input'], data['context'], hasManufacturingExtractor)

@chain
def extract_has_parameter(data):
    print("extract has_paramter relationships")
    return extract_relationships(data['input'], data['context'], hasParameterExtractor)



def validate_relationships(data, corrector_type):
    if data:
        corrector = corrector_type(data['nodes'], data['graph'], data['query'])
        corrector.run()
        print(corrector.validation_results)
        return corrector.corrected_graph
    return


@chain
def validate_has_property(data):
    print("validate_has_property")
    return validate_relationships(data, hasPropertyCorrector)


@chain
def validate_has_measurement(data):
    print("validate_has_measurement")
    return validate_relationships(data, hasMeasurementCorrector)


@chain
def validate_has_manufacturing(data):
    print("validate_has_manufacturing")
    return validate_relationships(data, hasManufacturingCorrector)


@chain
def validate_has_parameter(data):
    print("validate_has_parameter")
    return validate_relationships(data, hasParameterCorrector)




@chain
def build_results(data):
    print(data)
    relationships = []
    for key, value in data.items():
        if value is None:
            continue
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
        print('finished')
        print(self.relationships)
        return 'mau'
        return {"nodes": self.data["nodes"], "relationships": self.relationships}


