import os
import django

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mat2devplatform.settings')
django.setup()

import pandas as pd
from dotenv import load_dotenv
from graphutils.embeddings import request_embedding
from importing.models import NodeLabel, NodeLabelEmbedding, MatterAttribute, MatterAttributeEmbedding, \
    MeasurementAttribute, MeasurementAttributeEmbedding, ManufacturingAttribute, ManufacturingAttributeEmbedding, \
    PropertyAttribute, PropertyAttributeEmbedding, ParameterAttribute, ParameterAttributeEmbedding, MetadataAttribute, \
    MetadataAttributeEmbedding

# Mapping of the class names to actual class objects
class_mapping = {
    'NodeLabel': NodeLabel,
    'NodeLabelEmbedding': NodeLabelEmbedding,
    'MatterAttribute': MatterAttribute,
    'MatterAttributeEmbedding': MatterAttributeEmbedding,
    'MeasurementAttribute': MeasurementAttribute,
    'MeasurementAttributeEmbedding': MeasurementAttributeEmbedding,
    'ManufacturingAttribute': ManufacturingAttribute,
    'ManufacturingAttributeEmbedding': ManufacturingAttributeEmbedding,
    'PropertyAttribute': PropertyAttribute,
    'PropertyAttributeEmbedding': PropertyAttributeEmbedding,
    'ParameterAttribute': ParameterAttribute,
    'ParameterAttributeEmbedding': ParameterAttributeEmbedding,
    'MetadataAttribute': MetadataAttribute,
    'MetadataAttributeEmbedding': MetadataAttributeEmbedding,
}

class EmbeddingGenerator:
    def __init__(self, file_path):
        self.file_path = file_path  # Assuming data is a CSV format text

    def parse_data(self):
        # Parse the input data into a DataFrame
        df = pd.read_csv(self.file_path, header=None)
        df.columns = ['name', 'node_name', 'embedding_cls', 'node_cls']
        return df

    def create_embeddings(self, df):
        for index, row in df.iterrows():
            input_text = row['name']
            node_name = row['node_name']
            embedding_cls = row['embedding_cls']
            node_class = row['node_cls']
            print(input_text, node_name, embedding_cls, node_class)

            try:
                # Retrieve or create the embedding node
                try:
                    embedding_node = class_mapping[embedding_cls].nodes.get(input=input_text)
                except class_mapping[embedding_cls].DoesNotExist:
                    # If the node does not exist, create it
                    vector = request_embedding(input_text)
                    embedding_node = class_mapping[embedding_cls](input=input_text, vector=vector)
                    embedding_node.save()

                # Retrieve or create the label node
                try:
                    label_node = class_mapping[node_class].nodes.get(name=node_name)
                except class_mapping[node_class].DoesNotExist:
                    label_node = class_mapping[node_class](name=node_name)
                    label_node.save()

                # Check and create connections as necessary
                if not label_node.label.is_connected(embedding_node):
                    label_node.label.connect(embedding_node)

            except Exception as e:
                continue




if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    load_dotenv()
    from neomodel import config, MultipleNodesReturned

    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
    print(config.DATABASE_URL)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
    # Sample CSV data
    print(os.getcwd())
    directory = "./NodeAttributeExtraction/embedding_inputs/"
    #iterate over all csv files
    for file in os.listdir(directory):
        if file.endswith("matter_inputs.csv"):
            print(file)
            generator = EmbeddingGenerator(directory+file)
            df = generator.parse_data()
            generator.create_embeddings(df)
            print("Embeddings created and graph updated successfully.")

