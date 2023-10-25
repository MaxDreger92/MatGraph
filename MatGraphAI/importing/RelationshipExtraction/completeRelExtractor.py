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
from importing.importer import TableImporter
from importing.utils.openai import chat_with_gpt4
from mat2devplatform import settings


class fullRelationshipsExtractor:
    def __init__(self, input_json, api_key):
        self.input_json = input_json
        self.api_key = api_key

    def create_extractors(self):
        self.manufacturing_extractor = hasManufacturingExtractor(
            self.input_json, MATTER_MANUFACTURING_MESSAGE, chat_with_gpt4, ["matter"],
            ["manufacturing"], "Solar Cell fabrication", api_key=self.api_key
        )

        self.measurement_extractor = hasMeasurementExtractor(
            self.input_json, PROPERTY_MEASUREMENT_MESSAGE, chat_with_gpt4, ["measurement"], ["property"],
            "SolarCellFabrication", api_key=self.api_key
        )

        self.parameter_extractor = hasParameterExtractor(
            self.input_json, MANUFACTURING_PARAMETER_MESSAGE, chat_with_gpt4,
            ["manufacturing", "measurement"], ["parameter"], "SolarCellFabrication",
            api_key=self.api_key
        )

        self.property_extractor = hasPropertyExtractor(
            self.input_json, MATTER_PROPERTY_MESSAGE, chat_with_gpt4,
            ["matter"], ["property"], "SolarCellFabrication", api_key=self.api_key
        )

    def extract_relationships(self):
        # Ensure extractors are created
        self.create_extractors()

        relationships = [
            *self.parameter_extractor.run(),
            *self.measurement_extractor.run(),
            *self.manufacturing_extractor.run(),
            *self.property_extractor.run()
        ]

        return relationships

def generate_query(json_file):
    # Iterate through the list of nodes in the configuration
    query_parts = ["LOAD CSV FROM 'https://docs.google.com/spreadsheets/d/e/2PACX-1vT2wLudGdp-uSJ__NXR0lovJWP5gxA6EhyoVHtXQ7_DTLklpwIlA9ySMvF4ShZ6QE2ZSA1Dk7CPx6mu/pub?output=csv' AS row"]

    for node_config in json_file['nodes']:
        label = node_config['label']
        id = node_config['node_id']
        attributes = node_config['attributes']
        headers = json_file["headers"]
        # Construct the Cypher query for this node
        query_parts.append(
            f"CREATE (n{id}:{label} {{uid: randomUUID()}})")
        print(id)
        print(len(json_file["nodes"]))

        for attr_name, attr_values in attributes.items():
            for attr_config in attr_values:
                if attr_config['position'][1] == 'header':
                    # If the attribute value is in the header, use the attribute name directly
                    query_parts.append(f"""SET n{id}.{attr_name} = '{headers[attr_config['position'][0]]}'""")
                elif attr_config['position'][1] == 'column':
                    # If the attribute value is in a column, use the column index to access the value
                    query_parts.append(f"""SET n{id}.{attr_name} = row[{attr_config['position'][0]}]""")
    for rel in json_file['relationships']:
        rel_type = rel['rel_type']
        start_node = rel['connection'][0]
        end_node = rel['connection'][1]
        query_parts.append(f"""MERGE (n{start_node})-[r{start_node}{end_node}:{rel_type}]->(n{end_node})""")

    query = '\n'.join(query_parts)
    return query


def main():
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    load_dotenv()
    from neomodel import config

    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
    print(config.DATABASE_URL)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
    api_key = settings.OPENAI_API_KEY
    print(os.getcwd())
    ontology_folder = "/home/mdreger/Documents/MatGraphAI/Ontology/"
    file_name = "../../../data/materials.csv"
    # file_name = "../../../data/Absorption.csv"
    print(f"Testing relationship extraction for... \n {file_name} \n \n")
    input_json = (csv_to_json(file_name))
    json_obj = json.loads(str(input_json).replace('\'', '"'))
    json_obj['relationships'] = [{'rel_type': 'HAS_PARAMETER', 'connection': ['3', '11']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['3', '12']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['14', '21']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['14', '22']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['27', '34']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['27', '35']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['37', '44']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['37', '45']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['10', '3']}, {'rel_type': 'IS_MANFACTURING_OUTPUT', 'connection': ['3', '2']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['20', '14']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['47', '14']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['25', '14']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['23', '14']}, {'rel_type': 'IS_MANFACTURING_OUTPUT', 'connection': ['14', '13']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['33', '27']}, {'rel_type': 'IS_MANFACTURING_OUTPUT', 'connection': ['27', '26']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['43', '37']}, {'rel_type': 'IS_MANFACTURING_OUTPUT', 'connection': ['37', '36']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['2', '1']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['13', '1']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['26', '1']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['36', '1']}, {'rel_type': 'HAS_PROPERTY', 'connection': ['10', '15']}, {'rel_type': 'HAS_PROPERTY', 'connection': ['13', '16']}]

    # pprint(json.loads(str(input_json).replace('\'', '"')), indent = 4)
    importer = TableImporter(json_obj)
    importer.run()
    # print(generate_query(json_obj))
    manufacturing_extractor = hasManufacturingExtractor(input_json, MATTER_MANUFACTURING_MESSAGE, chat_with_gpt4, ["matter"],
                                             ["manufacturing"], "Solar Cell fabrication", api_key=api_key)
    measurement_extractor = hasMeasurementExtractor(input_json, PROPERTY_MEASUREMENT_MESSAGE, chat_with_gpt4, ["measurement"], ["property"],
                                        "SolarCellFabrication", api_key=api_key)

    parameter_extractor = hasParameterExtractor(input_json, MANUFACTURING_PARAMETER_MESSAGE, chat_with_gpt4,
                                                ["manufacturing", "measurement"], ["parameter"], "SolarCellFabrication",
                                                api_key)
    property_extractor = hasPropertyExtractor(input_json, MATTER_PROPERTY_MESSAGE, chat_with_gpt4,
                                              ["matter"], ["property"], "SolarCellFabrication", api_key)
    relationships = [
        # *parameter_extractor.run(),
        # *measurement_extractor.run(),
        # *manufacturing_extractor.run(),
        # *property_extractor.run()
    ]
    print(relationships)




if __name__ == "__main__":
    main()
