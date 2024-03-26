from importing.RelationshipExtraction.examples import MATTER_PROPERTY_EXAMPLES
from importing.RelationshipExtraction.input_generator import prepare_lists
from importing.RelationshipExtraction.relationshipExtractor import relationshipExtractor
from importing.RelationshipExtraction.schema import HasPropertyRelationships
from importing.RelationshipExtraction.setupMessages import MATTER_PROPERTY_MESSAGE
from importing.utils.openai import chat_with_gpt4


class hasPropertyExtractor(relationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation = []
        self.schema = HasPropertyRelationships
        self.setup_message = MATTER_PROPERTY_MESSAGE
        self.label_one = ["matter"]
        self.label_two = ["property"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)
        self.examples = MATTER_PROPERTY_EXAMPLES


