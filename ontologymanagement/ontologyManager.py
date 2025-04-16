import ast
from json import JSONDecodeError
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import hdbscan
from sklearn.cluster import KMeans
import numpy as np
from django.conf import settings
from dotenv import load_dotenv
from langchain.chains.ernie_functions import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI
from neomodel import db
from owlready2 import *
from owlready2 import get_ontology, Thing

from graphutils.config import CHAT_GPT_MODEL
from graphutils.embeddings import request_embedding
from graphutils.models import AlternativeLabel
from matgraph.models.embeddings import MatterEmbedding, ProcessEmbedding, QuantityEmbedding
from matgraph.models.ontology import EMMOMatter, EMMOQuantity, EMMOProcess
from ontologymanagement.schema import OntologyClass
from ontologymanagement.setupMessages import MATTER_ONTOLOGY_ASSISTANT_MESSAGES, QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES, \
    PROCESS_ONTOLOGY_ASSISTANT_MESSAGES


def convert_alternative_labels(onto):
    onto_path = os.path.join("/home/mdreger/Documents/MatGraphAI/Ontology/", onto)
    onto_path_alt = os.path.join("/home/mdreger/Documents/MatGraphAI/Ontology/alt_list", onto)
    ontology = get_ontology(onto_path_alt).load()

    # Define the new alternative_label property
    # Define the new alternative_label property
    with ontology:
        class alternative_label(AnnotationProperty):
            domain = [Thing]
            range = [str]

        # Iterate over all classes in the ontology
        for cls in ontology.classes():
            # If the class has the 'alternative_labels' property
            if cls.alternative_labels:
                # Retrieve the alternative_labels value, parse it, and remove the property
                alt_labels = list(
                    cls.alternative_labels[0].replace("[", "").replace("]", "").replace("'", "").split(","))
                # cls.alternative_labels = []
                for l in alt_labels:
                    label = l.strip()
                    label = re.sub(r'\W+', '', label)
                    cls.alternative_label.append(label)  # Make sure to use the newly defined property

        ontology.save(onto_path, format="rdfxml")


class OntologyManager:
    def __init__(self, ontology_folder="/home/mdreger/Documents/MatGraphAI/Ontology/"):
        self.ontology_folder = ontology_folder
        self.file_to_model = {
            "matter.owl": EMMOMatter,
            "quantities.owl": EMMOQuantity,
            "manufacturing.owl": EMMOProcess}
        # self.EXAMPLES = {
        #     "material.owl": MATTER_ONTOLOGY_ASSISTANT_EXAMPLES,
        #     "quantities.owl": QUANTITY_ONTOLOGY_ASSISTANT_EXAMPLES,
        #     "manufacturing.owl": PROCESS_ONTOLOGY_ASSISTANT_EXAMPLES,
        # }
        self.SETUP_MESSAGE = {
            "material.owl": MATTER_ONTOLOGY_ASSISTANT_MESSAGES,
            "quantities.owl": QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES,
            "manufacturing.owl": PROCESS_ONTOLOGY_ASSISTANT_MESSAGES,
        }

    def get_labels(self, class_name, setup_message, examples=None):
        """Performs the initial extraction of relationships using GPT-4."""

        llm = ChatOpenAI(model_name=CHAT_GPT_MODEL, openai_api_key=os.getenv("OPENAI_API_KEY"))
        setup_message = setup_message
        prompt = ChatPromptTemplate.from_messages(setup_message)

        if examples:
            print("Examples provided")
            print(examples)
            example_prompt = ChatPromptTemplate.from_messages([('human', "{input}"), ('ai', "{output}")])
            few_shot_prompt = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=examples)
            prompt = ChatPromptTemplate.from_messages([setup_message[0], few_shot_prompt, *setup_message[1:]])

        chain = create_structured_output_runnable(OntologyClass, llm, prompt).with_config(
            {"run_name": f"{label}-generation"})
        ontology_class = chain.invoke({"input": class_name})
        return ontology_class

    def update_ontology(self, ontology_file):
        if ontology_file == "matter.owl":
            return


        ontology_path1 = os.path.join(self.ontology_folder, ontology_file)
        ontology_path = os.path.join(self.ontology_folder, ontology_file)

        onto = get_ontology(ontology_path).load()
        with onto:
            class alternative_label(AnnotationProperty):
                domain = [Thing]
                range = [str]
            class onto_name(AnnotationProperty):
                domain = [Thing]
                range = [str]
            class description_name(AnnotationProperty):
                domain = [Thing]
                range = str
            for cls in onto.classes():
                if not cls.onto_name:
                    print(f"Need to update class: {cls.name}")
                try:
                    output = self.get_labels(cls.name, self.SETUP_MESSAGE[ontology_file])
                    print(cls.name, output.name, output.alternative_labels)
                    cls.alternative_labels = str(output.alternative_labels)
                    cls.onto_name = cls.name
                    cls.description_name = output.description.replace("'", "")
                except JSONDecodeError:
                    print(f"Invalid JSON response for class: {cls.name}")

            onto.save(ontology_path1, format="rdfxml")

    def import_to_neo4j(self, ontology_file):

        ontology_path = os.path.join(self.ontology_folder, ontology_file)
        onto = get_ontology(ontology_path).load()

        with onto:
            pass

        for cls in onto.classes():

            class_name = str(cls.name).title()
            class_uri = str(cls.iri)
            class_comment = str(cls.comment).replace("'","").replace("[","").replace("]","") if cls.comment else None
            print(cls.name)
            try:
                cls_instance = self.file_to_model[ontology_file].nodes.get(uri=class_uri)
                cls_instance.name = class_name.title()
                cls_instance.validated_labels = True
                cls_instance.validated_ontology = True
                cls_instance.description = class_comment
                cls_instance.save()
            except:
                cls_instance = self.file_to_model[ontology_file](uri=class_uri, name=class_name,
                                                                 description=class_comment)
                cls_instance.save()
            EMBEDDING_MODEL_MAPPER = {
                "matter.owl": MatterEmbedding,
                "quantities.owl": QuantityEmbedding,
                "manufacturing.owl": ProcessEmbedding
            }
            try:
                embedding_name = EMBEDDING_MODEL_MAPPER[ontology_file].nodes.get(input=class_name)
                embedding_description = EMBEDDING_MODEL_MAPPER[ontology_file].nodes.get(input=class_comment)
                if not cls_instance.is_connected(embedding_node):
                    secondary_embedding_name = EMBEDDING_MODEL_MAPPER[ontology_file](input=embedding_name.input,
                                                                                      vector=embedding_name.vector)
                    secondary_embedding_description = EMBEDDING_MODEL_MAPPER[ontology_file](input=embedding_description.input,
                                                                                             vector=embedding_description.vector)
                    cls_instance.model_embedding.connect(secondary_embedding_name)
                    cls_instance.model_embedding.connect(secondary_embedding_description)
            except:
                vector_name = request_embedding(class_name)
                embedding_name = EMBEDDING_MODEL_MAPPER[ontology_file](vector=vector_name, input=class_name).save()
                cls_instance.model_embedding.connect(embedding_name)
                vector_description = request_embedding(class_comment)
                embedding_description = EMBEDDING_MODEL_MAPPER[ontology_file](vector=vector_description,
                                                                              input=class_comment).save()
                cls_instance.model_embedding.connect(embedding_description)
            if cls.alternative_labels:

                for label in ast.literal_eval(cls.alternative_labels[0]):
                    alt_label = str(label)
                    label = label.title()
                    try:
                        alternative_label_node = AlternativeLabel.nodes.get(label=alt_label)
                        if not cls_instance.alternative_label.is_connected(alternative_label_node):
                            secondary_label_node = AlternativeLabel(label=alt_label)
                            secondary_label_node.save()
                            cls_instance.alternative_label.connect(secondary_label_node)
                    except:
                        alternative_label_node = AlternativeLabel(label=alt_label)
                        alternative_label_node.save()
                        cls_instance.alternative_label.connect(alternative_label_node)
                    try:
                        embedding_node = EMBEDDING_MODEL_MAPPER[ontology_file](input=label)
                        if not cls_instance.is_connected(embedding_node):
                            secondary_embedding_node =EMBEDDING_MODEL_MAPPER[ontology_file](input= embedding_node.input, vector=embedding_node.vector)
                            cls_instance.model_embedding.connect(secondary_embedding_node)
                    except:
                        vector = request_embedding(label)
                        embedding_node = EMBEDDING_MODEL_MAPPER[ontology_file](vector=vector, input=label).save()
                        cls_instance.model_embedding.connect(embedding_node)

            # Add subclass relationships
            for subclass in cls.subclasses():
                subclass_name = str(subclass.name)
                subclass_uri = str(subclass.iri)
                subclass_comment = str(subclass.comment) if subclass.comment else None
                # print(f"Creating subclass_instance with kwargs: {subclass_name=}, {subclass_comment=}, {subclass_uri=}")
                try:
                    subclass_instance = self.file_to_model[ontology_file].nodes.get(uri=subclass_uri)
                    subclass_instance.name = subclass_name
                    subclass_instance.description = subclass_comment
                    subclass_instance.save()
                    subclass_instance.emmo_subclass.connect(cls_instance)

                except:
                    subclass_instance = self.file_to_model[ontology_file](uri=subclass_uri, name=subclass_name,
                                                                          description=subclass_comment)
                    subclass_instance.save()
                    subclass_instance.emmo_subclass.connect(cls_instance)

    def update_all_ontologies(self):
        ontologies = [f for f in os.listdir(self.ontology_folder) if f.endswith(".owl")]
        for ontology_file in ontologies:
            self.update_ontology(ontology_file)

    def import_all_ontologies(self):
        ontologies = [f for f in os.listdir(self.ontology_folder) if f.endswith(".owl")]
        for ontology_file in ontologies:
            self.import_to_neo4j(ontology_file)

# def get_embeddings(type):
#     """
#     Connects to Neo4j and retrieves embeddings along with their node types.
#     Make sure your nodes have an "embedding" property and a label indicating the node type.
#     """
#     query = f"""
#     MATCH (n:{type})-[:FOR]-(m)
#     WHERE size(n.input) < 30
#
#     RETURN n.vector AS embedding, labels(n) AS node_type, m.name AS name
#     """
#     output = db.cypher_query(query)
#     return output[0]
#
# def main():
#     # Get the project root directory
#     project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
#     # Change the current working directory to the project root directory
#     os.chdir(project_root)
#
#     load_dotenv()
#     from neomodel import config
#
#     config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
#     print(config.DATABASE_URL)
#
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
#     api_key = settings.OPENAI_API_KEY
#     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     ontology_folder = BASE_DIR + "/Ontology/"
#
#     ontology_manager = OntologyManager(ontology_folder)
#     # ontology_manager.update_ontology("quantities.owl")
#     # ontology_manager.import_to_neo4j("quantities.owl")
#     # ontology_manager.update_ontology("matter.owl")
#     # ontology_manager.import_to_neo4j("matter.owl")
#     # ontology_manager.update_ontology("manufacturing.owl")
#     # ontology_manager.import_to_neo4j("manufacturing.owl")
#
#     # from emmopy import get_emmo
#     uid = EMMOMatter.nodes.get_by_string(string = "ModelEmbedding", limit = 10)[0]
#     print(uid.name)
#     data = get_embeddings(type="ModelEmbedding")
#
#
#     if not data:
#         print("No embeddings found in the database!")
#         return
#
#     # Separate embeddings and node types.
#     embeddings = np.array([d[0] for d in data])
#     node_types = []
#     for d in data:
#         # d[1] is a list of labels; choose the first label that isn't "ModelEmbedding".
#         node_type = next((label for label in d[1] if label != "ModelEmbedding"), "ModelEmbedding")
#         node_types.append(node_type)
#     plt.style.use("ggplot")
#     # Step 1: Normalize the embeddings using L2 normalization
#     # # Normalize the embeddings using L2 normalization
#     # embeddings_norm = normalize(embeddings, norm="l2")
#     #
#     # # Reduce dimensionality to 2D using PCA
#     # pca_2d = PCA(n_components=2, random_state=42)
#     # embeddings_2d = pca_2d.fit_transform(embeddings_norm)
#     #
#     # # Prepare the plot
#     # unique_types = sorted(set(node_types))
#     # cmap = plt.cm.get_cmap("viridis", len(unique_types))
#     #
#     # plt.figure(figsize=(10, 8))
#     # for idx, node_type in enumerate(unique_types):
#     #     indices = [i for i, t in enumerate(node_types) if t == node_type]
#     #     plt.scatter(
#     #         embeddings_2d[indices, 0],
#     #         embeddings_2d[indices, 1],
#     #         label=node_type,
#     #         color=cmap(idx),
#     #         s=20  # Smaller point size
#     #     )
#     #
#     # plt.title("2D Visualization of OpenAI Embeddings by Node Type", fontsize=14, pad=20)
#     # plt.xlabel("PCA Component 1", labelpad=10)
#     # plt.ylabel("PCA Component 2", labelpad=10)
#     # plt.legend(title="Node Type", fontsize=9, title_fontsize=10)
#     # plt.show()
#     # Normalize the embeddings using L2 normalization
#     embeddings_norm = normalize(embeddings, norm="l2")
#
#     # Reduce dimensionality to 2D using PCA
#     pca_2d = PCA(n_components=2, random_state=42)
#     embeddings_2d = pca_2d.fit_transform(embeddings_norm)
#
#     # Get sorted unique node types (assuming there are three)
#     unique_types = sorted(set(node_types))
#
#     # Create a figure with three subplots (one per node type)
#     fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharex=True, sharey=True)
#
#     for ax, node_type in zip(axes, unique_types):
#         # Filter indices for the current node type
#         indices = [i for i, t in enumerate(node_types) if t == node_type]
#         # Scatter plot for the current node type
#         ax.scatter(embeddings_2d[indices, 0],
#                    embeddings_2d[indices, 1],
#                    s=20)  # Smaller point size
#         ax.set_title(f"Node Type: {node_type}", fontsize=12)
#         ax.set_xlabel("PCA Component 1", labelpad=10)
#         ax.set_ylabel("PCA Component 2", labelpad=10)
#
#     plt.suptitle("2D Visualization of OpenAI Embeddings by Node Type", fontsize=16, y=1.05)
#     plt.tight_layout()
#     plt.show()
#
# if __name__ == "__main__":
#     main()


def get_embeddings(type):
    """
    Connects to Neo4j and retrieves embeddings along with their node types and names.
    Make sure your nodes have an "embedding" property and a label indicating the node type.
    """
    query = f"""
    MATCH (n:{type})-[:FOR]-(m)
    WHERE size(n.input) < 30
    RETURN n.vector AS embedding, labels(n) AS node_type, m.name AS name
    """
    output = db.cypher_query(query)
    return output[0]

def main():
    # Set project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    load_dotenv()
    from neomodel import config
    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
    print(config.DATABASE_URL)

    # Set up Django settings if needed
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
    from django.conf import settings  # Assuming Django settings are needed for OPENAI_API_KEY
    api_key = settings.OPENAI_API_KEY

    # Initialize ontology manager or any other required objects here
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ontology_folder = BASE_DIR + "/Ontology/"
    # ontology_manager = OntologyManager(ontology_folder)
    # ... additional ontology setup code ...

    # Fetch embeddings from Neo4j
    data = get_embeddings(type="ModelEmbedding")
    if not data:
        print("No embeddings found in the database!")
        return

    # Separate embeddings and node types.
    embeddings = np.array([d[0] for d in data])
    node_types = []
    for d in data:
        # d[1] is a list of labels; choose the first label that isn't "ModelEmbedding".
        node_type = next((label for label in d[1] if label != "ModelEmbedding"), "ModelEmbedding")
        node_types.append(node_type)

    # Normalize embeddings using L2 normalization
    embeddings_norm = normalize(embeddings, norm="l2")

    # Reduce embeddings to 2D using PCA for visualization
    pca_2d = PCA(n_components=2, random_state=42)
    embeddings_2d = pca_2d.fit_transform(embeddings_norm)

    # Get sorted unique node types (assumed three in this case)
    unique_types = sorted(set(node_types))

    # Set a stylish theme for the plot
    plt.style.use("ggplot")

    # Create a figure with subplots (one for each node type)
    fig, axes = plt.subplots(1, len(unique_types), figsize=(18, 6), sharex=True, sharey=True)

    for ax, node_type in zip(axes, unique_types):
        # Get indices for the current node type
        indices = [i for i, t in enumerate(node_types) if t == node_type]
        # For these indices, extract the names
        names = [data[i][2] for i in indices]
        unique_names = sorted(set(names))

        # Use the full continuous Viridis colormap
        cmap_names = plt.cm.viridis

        # Plot points for each unique name with a distinct color
        for j, name in enumerate(unique_names):
            # Normalize j to a value between 0 and 1
            norm_val = j / max(1, len(unique_names) - 1)
            name_indices = [i for i in indices if data[i][2] == name]
            ax.scatter(embeddings_2d[name_indices, 0],
                       embeddings_2d[name_indices, 1],
                       s=20,  # Smaller point size
                       color=cmap_names(norm_val))

        ax.set_title(f"Node Type: {node_type}", fontsize=12)
        ax.set_xlabel("PCA Component 1", labelpad=10)
        ax.set_ylabel("PCA Component 2", labelpad=10)

    plt.suptitle("2D Visualization of OpenAI Embeddings by Node Type (Colored by Name)", fontsize=16, y=1.05)
    plt.tight_layout()
    plt.show()
if __name__ == "__main__":
    main()
