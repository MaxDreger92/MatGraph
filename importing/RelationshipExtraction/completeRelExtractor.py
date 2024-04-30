import json

import django

from importing.RelationshipExtraction.relationshipCorrector import hasParameterCorrector, hasPropertyCorrector, \
    hasManufacturingCorrector, hasMeasurementCorrector, hasPartMatterCorrector, hasPartManufacturingCorrector, \
    hasPartMeasurementCorrector
from importing.RelationshipExtraction.relationshipExtractor import HasParameterExtractor, HasManufacturingExtractor, \
    HasMeasurementExtractor, HasPropertyExtractor, HasPartMatterExtractor, HasPartManufacturingExtractor, \
    HasPartMeasurementExtractor

django.setup()

from langchain_core.runnables import chain, RunnableParallel






def extract_relationships(input_json, context, header, first_line, extractor_type):
    extractor = extractor_type(input_json, context, header, first_line)
    if len(extractor.label_one_nodes) != 0  and len(extractor.label_two_nodes) != 0 :
        extractor.run()
        return extractor.results
    return None

@chain
def extract_has_property(data):
    print(data['input'])
    return extract_relationships(data['input'], data['context'], data['header'], data['first_line'], HasPropertyExtractor)


@chain
def extract_has_measurement(data):
    return extract_relationships(data['input'], data['context'], data['header'], data['first_line'], HasMeasurementExtractor)

@chain
def extract_has_manufacturing(data):
    return extract_relationships(data['input'], data['context'], data['header'], data['first_line'], HasManufacturingExtractor)

@chain
def extract_has_parameter(data):
    return extract_relationships(data['input'], data['context'], data['header'], data['first_line'], HasParameterExtractor)

@chain
def extract_has_part_matter(data):
    return extract_relationships(data['input'], data['context'], data['header'], data['first_line'], HasPartMatterExtractor)

@chain
def extract_has_part_manufacturing(data):
    return extract_relationships(data['input'], data['context'], data['header'], data['first_line'], HasPartManufacturingExtractor)

@chain
def extract_has_part_measurement(data):
    return extract_relationships(data['input'], data['context'], data['header'], data['first_line'], HasPartMeasurementExtractor)


# @chain
# def extract_has_metadata(data):
#     print("extract has_metadata relationships")
#     return extract_relationships(data['input'], data['context'], hasParameterCorrector)



def validate_relationships(data, corrector_type):
    if data:
        corrector = corrector_type(data['nodes'], data['graph'], data['query'])
        corrector.run()
        print(corrector.validation_results)
        return corrector.corrected_graph
    return


@chain
def validate_has_property(data):
    return validate_relationships(data, hasPropertyCorrector)


@chain
def validate_has_measurement(data):
    return validate_relationships(data, hasMeasurementCorrector)


@chain
def validate_has_manufacturing(data):
    return validate_relationships(data, hasManufacturingCorrector)


@chain
def validate_has_parameter(data):
    return validate_relationships(data, hasParameterCorrector)

@chain
def validate_has_metadata(data):
    return validate_relationships(data, hasParameterCorrector)

@chain
def validate_has_part_matter(data):
    return validate_relationships(data, hasPartMatterCorrector)

@chain
def validate_has_part_manufacturing(data):
    return validate_relationships(data, hasPartManufacturingCorrector)

@chain
def validate_has_part_measurement(data):
    return validate_relationships(data, hasPartMeasurementCorrector)


@chain
def build_results(data):
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
    def __init__(self, input_json, context, header, first_line, *args, **kwargs):
        self.header = header
        self.first_line = first_line
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
            has_parameter=extract_has_parameter | validate_has_parameter,
            # has_part_matter = extract_has_part_matter | validate_has_part_matter,
            # has_part_manufacturing = extract_has_part_manufacturing | validate_has_part_manufacturing,
            # has_part_measurement = extract_has_part_measurement | validate_has_part_measurement
            # has_metadata=extract_has_metadata | validate_has_metadata
        ) | build_results
        chain = chain.with_config({"run_name": "relationship-extraction"})
        self.relationships = chain.invoke({
            'input': self.data,
            'context': self.context,
            'header': self.header,
            'first_line': self.first_line
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


