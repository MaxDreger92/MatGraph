from json import JSONDecodeError

from django.conf import settings
from dotenv import load_dotenv
from langchain_core.prompts import FewShotChatMessagePromptTemplate, AIMessagePromptTemplate, \
    SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
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
        self.EMBEDDING_MODEL_MAPPER = {
            "matter.owl":  MatterEmbedding,   # or MatterEmbedding
            "quantities.owl": QuantityEmbedding,
            "manufacturing.owl": ProcessEmbedding
        }
        self.SETUP_MESSAGE = {
            "material.owl": MATTER_ONTOLOGY_ASSISTANT_MESSAGES,
            "quantities.owl": QUANTITY_ONTOLOGY_ASSISTANT_MESSAGES,
            "manufacturing.owl": PROCESS_ONTOLOGY_ASSISTANT_MESSAGES,
        }


    def get_labels(self, class_name, setup_message, examples=None):
        """Performs the initial extraction of relationships using GPT-4."""
        llm = ChatOpenAI(
            model_name=CHAT_GPT_MODEL,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=1
        )

        # Step 1: Convert each (role, text) in `setup_message` to a MessagePromptTemplate
        prompt_templates = []
        for role, text in setup_message:
            if role == "system":
                prompt_templates.append(SystemMessagePromptTemplate.from_template(text))
            elif role == "assistant":
                prompt_templates.append(AIMessagePromptTemplate.from_template(text))
            else:  # treat everything else as a 'user' prompt
                prompt_templates.append(HumanMessagePromptTemplate.from_template(text))



        # Step 3: If you have few-shot examples with "input" and "output":
        if examples:
            # examples should be a list of dicts like:
            # [{"input": "Example user prompt", "output": "Ideal example answer"}, ...]
            print("EXAMLES", examples)
            example_prompt = ChatPromptTemplate.from_messages([
                HumanMessagePromptTemplate.from_template("{input}"),
                AIMessagePromptTemplate.from_template("{output}")
            ])
            few_shot_prompt = FewShotChatMessagePromptTemplate(
                example_prompt=example_prompt,
                examples=examples,
            )

            # Optionally insert the few-shot prompt before the final user request
            # so that the model sees the examples first:
            prompt_templates.insert(len(prompt_templates) - 2, few_shot_prompt)
        # Step 4: Build the overall ChatPromptTemplate from all pieces
        prompt = ChatPromptTemplate.from_messages(prompt_templates)

        # Step 5: Format the prompt messages with class_name
        messages = prompt.format_messages(input=class_name)

        # Step 6: Run the chain with structured output
        chain = llm.with_structured_output(OntologyClass)
        ontology_class = chain.invoke(messages)
        print(ontology_class)
        return ontology_class

    def update_ontology(self, ontology_file):

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
        """
        Main entry point to import an ontology into Neo4j.
        """
        ontology_path = os.path.join(self.ontology_folder, ontology_file)
        onto = get_ontology(ontology_path).load()

        with onto:
            pass

        for cls in onto.classes():
            self._process_ontology_class(cls, ontology_file)

    def _process_ontology_class(self, cls, ontology_file, parent_instance=None):
        """
        Recursively processes a single ontology class:
         - Creates/updates its node
         - Creates/updates alternative labels (and their embeddings)
         - Creates/updates embeddings for the class name and comment
         - Recursively processes its subclasses
        """
        # 1. Create or update the current class node in Neo4j
        cls_instance = self._create_or_update_class(cls, ontology_file)

        # 2. Handle alternative labels (including embedding creation for each label)
        self._handle_alternative_labels(cls, cls_instance, ontology_file)

        # 3. Handle embeddings for this class (name + comment)
        self._handle_embeddings(cls_instance, cls, ontology_file)

        # 4. Connect to parent if any
        if parent_instance and not cls_instance.emmo_subclass.is_connected(parent_instance):
            cls_instance.emmo_subclass.connect(parent_instance)

        # 5. Recursively handle subclasses
        for subclass in cls.subclasses():
            self._process_ontology_class(subclass, ontology_file, cls_instance)

    def _create_or_update_class(self, cls, ontology_file):
        """
        Creates or updates a class node in Neo4j based on the OWL class.
        Uses get_or_none to avoid duplicates.
        """
        ModelClass = self.file_to_model[ontology_file]

        class_name = str(cls.name).title()
        class_uri = str(cls.iri)
        class_comment = (
            str(cls.comment).replace("'", "").replace("[", "").replace("]", "")
            if cls.comment
            else None
        )

        print(f"Processing class: {cls.name}")

        # Attempt to find an existing node by URI
        cls_instance = ModelClass.nodes.get_or_none(uri=class_uri)
        if cls_instance:
            # Update existing node
            cls_instance.name = class_name
            cls_instance.description = class_comment
            cls_instance.validated_labels = True
            cls_instance.validated_ontology = True
            cls_instance.save()
        else:
            # Create a new node
            cls_instance = ModelClass(
                uri=class_uri,
                name=class_name,
                description=class_comment,
                validated_labels=True,
                validated_ontology=True
            )
            cls_instance.save()

        return cls_instance

    def _handle_alternative_labels(self, cls, cls_instance, ontology_file):
        """
        Safely parses and connects alternative labels for the class node.
        Also creates embeddings for each alternative label.
        """
        if not cls.alternative_labels:
            print(f"No alternative labels for class: {cls_instance.name}")
            return

        raw_labels = cls.alternative_labels[0]
        labels = self._parse_labels(raw_labels) or [raw_labels]

        for label in labels:
            alt_label_str = str(label)
            print(f"Alternative label: {alt_label_str}")

            # 1) Create/find AlternativeLabel node
            try:
                alternative_label_node = AlternativeLabel.nodes.get(label=alt_label_str)
            except AlternativeLabel.DoesNotExist:
                alternative_label_node = AlternativeLabel(label=alt_label_str)
                alternative_label_node.save()

            # 2) Connect the AlternativeLabel if not already connected
            if not cls_instance.alternative_label.is_connected(alternative_label_node):
                cls_instance.alternative_label.connect(alternative_label_node)

            # 3) (Optional) Create/find embedding node for this alternative label
            EmbeddingModel = self.EMBEDDING_MODEL_MAPPER.get(ontology_file)
            if EmbeddingModel:  # If we have a valid embedding class
                alt_embedding_node = EmbeddingModel.nodes.get_or_none(input=alt_label_str)
                if alt_embedding_node is None:
                    vector_alt_label = request_embedding(alt_label_str)
                    alt_embedding_node = EmbeddingModel(input=alt_label_str,
                                                        vector=vector_alt_label).save()

                # Connect if not already connected
                if not cls_instance.model_embedding.is_connected(alt_embedding_node):
                    cls_instance.model_embedding.connect(alt_embedding_node)

    def _parse_labels(self, raw_labels_str):
        """
        Tries to parse raw labels from either a Python literal or JSON.
        Returns a list of labels or an empty list if parsing fails.
        """
        import ast
        import json

        try:
            labels = ast.literal_eval(raw_labels_str)
            if not isinstance(labels, list):
                labels = [labels]
            return labels
        except Exception as e:
            print(f"Error evaluating alternative labels via literal_eval: {e}")

        try:
            labels = json.loads(raw_labels_str)
            if not isinstance(labels, list):
                labels = [labels]
            return labels
        except Exception as json_e:
            print(f"JSON parsing failed as well: {json_e}")

        return []

    def _handle_embeddings(self, cls_instance, cls, ontology_file):
        """
        Creates/gets and connects embedding nodes for class name and comment.
        """
        class_name = str(cls.name)
        class_comment = str(cls.comment) if cls.comment else ""

        EmbeddingModel = self.EMBEDDING_MODEL_MAPPER.get(ontology_file)
        if not EmbeddingModel:
            # If no embedding model is mapped for this file, skip
            return

        # --- Embedding for class name ---
        embedding_node_name = EmbeddingModel.nodes.get_or_none(input=class_name)
        if embedding_node_name is None:
            vector_name = request_embedding(class_name)
            embedding_node_name = EmbeddingModel(input=class_name,
                                                 vector=vector_name).save()

        if not cls_instance.model_embedding.is_connected(embedding_node_name):
            cls_instance.model_embedding.connect(embedding_node_name)

        # --- Embedding for class comment ---
        if class_comment:
            embedding_node_comment = EmbeddingModel.nodes.get_or_none(input=class_comment)
            if embedding_node_comment is None:
                vector_comment = request_embedding(class_comment)
                embedding_node_comment = EmbeddingModel(input=class_comment,
                                                        vector=vector_comment).save()

            if not cls_instance.model_embedding.is_connected(embedding_node_comment):
                cls_instance.model_embedding.connect(embedding_node_comment)

    def update_all_ontologies(self):
        ontologies = [f for f in os.listdir(self.ontology_folder) if f.endswith(".owl")]
        for ontology_file in ontologies:
            self.update_ontology(ontology_file)

    def import_all_ontologies(self):
        ontologies = [f for f in os.listdir(self.ontology_folder) if f.endswith(".owl")]
        for ontology_file in ontologies:
            self.import_to_neo4j(ontology_file)


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
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ontology_folder = BASE_DIR + "/Ontology/"

    ontology_manager = OntologyManager(ontology_folder)
    # ontology_manager.update_ontology("quantities.owl")
    # ontology_manager.update_ontology("quantities.owl")
    # ontology_manager.update_ontology("matter.owl")
    # ontology_manager.update_ontology("matter.owl")
    # ontology_manager.update_ontology("manufacturing.owl")
    # ontology_manager.update_ontology("manufacturing.owl")
    ontology_manager.import_to_neo4j("manufacturing.owl")
    ontology_manager.import_to_neo4j("matter.owl")
    ontology_manager.import_to_neo4j("quantities.owl")

    # from emmopy import get_emmo


if __name__ == "__main__":
    main()
