from importing.RelationshipExtraction.examples import HAS_PARAMETER_EXAMPLES
from importing.RelationshipExtraction.input_generator import prepare_lists
from importing.RelationshipExtraction.relationshipExtractor import relationshipExtractor
from importing.RelationshipExtraction.schema import HasParameterRelationships
from importing.RelationshipExtraction.setupMessages import HAS_PARAMETER_MESSAGE
from importing.utils.openai import chat_with_gpt4


class hasParameterExtractor(relationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.conversation = []
        self.schema = HasParameterRelationships
        self.setup_message = HAS_PARAMETER_MESSAGE
        self.label_one = ["manufacturing", "measurement"]
        self.label_two = ["parameter"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)
        self.examples = HAS_PARAMETER_EXAMPLES




