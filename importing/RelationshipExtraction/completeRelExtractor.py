import json
import os
from pprint import pprint
import django
django.setup()
from dotenv import load_dotenv

from importing.RelationshipExtraction.hasManufacturingExtractor import hasManufacturingExtractor
from importing.RelationshipExtraction.hasMeasurementExtractor import hasMeasurementExtractor
from importing.RelationshipExtraction.hasParameterExtractor import hasParameterExtractor
from importing.RelationshipExtraction.hasPropertyExtractor import hasPropertyExtractor
from importing.RelationshipExtraction.input_generator import csv_to_json
from importing.RelationshipExtraction.setupMessages import MANUFACTURING_PARAMETER_MESSAGE, \
    MATTER_MANUFACTURING_MESSAGE, PROPERTY_MEASUREMENT_MESSAGE, MATTER_PROPERTY_MESSAGE
from importing.utils.openai import chat_with_gpt4
from mat2devplatform import settings


class fullRelationshipsExtractor:
    def __init__(self, input_json, context):
        self.input_json = input_json
        self.context = context

    def create_extractors(self):
        self.manufacturing_extractor = hasManufacturingExtractor(
            self.input_json, MATTER_MANUFACTURING_MESSAGE, chat_with_gpt4, ["matter"],
            ["manufacturing"], self.context
        )

        self.measurement_extractor = hasMeasurementExtractor(
            self.input_json, PROPERTY_MEASUREMENT_MESSAGE, chat_with_gpt4, ["measurement"], ["property"],
            self.context
        )

        self.parameter_extractor = hasParameterExtractor(
            self.input_json, MANUFACTURING_PARAMETER_MESSAGE, chat_with_gpt4,
            ["manufacturing", "measurement"], ["parameter"], self.context
        )

        self.property_extractor = hasPropertyExtractor(
            self.input_json, MATTER_PROPERTY_MESSAGE, chat_with_gpt4,
            ["matter"], ["property"], self.context
        )

    def run(self):
        # Ensure extractors are created
        self.create_extractors()

        self._relationships = [
            *self.parameter_extractor.run(),
            *self.measurement_extractor.run(),
            *self.manufacturing_extractor.run(),
            *self.property_extractor.run()
        ]
        # self._relationships = [{'rel_type': 'HAS_PARAMETER', 'connection': ['0', '18']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['1', '20']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['2', '21']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['3', '23']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['4', '26']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['5', '28']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['6', '33']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['7', '0']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['8', '1']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['10', '2']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['11', '3']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['12', '4']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['13', '0']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['14', '1']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['15', '2']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['16', '3']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['17', '4']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['18', '5']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['19', '5']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['20', '6']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['21', '6']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['0', '9']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['1', '18']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['2', '9']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['3', '18']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['4', '9']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['5', '20']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['6', '20']}]


    @property
    def relationships(self):
        return self._relationships
    @property
    def results(self):
        self.input_json = json.loads(self.input_json)
        return {"nodes": self.input_json["nodes"], "relationships": self.relationships}



