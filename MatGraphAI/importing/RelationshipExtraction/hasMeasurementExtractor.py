from importing.RelationshipExtraction.input_generator import prepare_lists
from importing.RelationshipExtraction.relationshipExtractor import relationshipExtractor
from importing.RelationshipExtraction.schema import HasMeasurementRelationships
from importing.RelationshipExtraction.setupMessages import PROPERTY_MEASUREMENT_MESSAGE
from importing.utils.openai import chat_with_gpt4


class hasMeasurementExtractor(relationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation = []
        self.schema = HasMeasurementRelationships
        self.setup_message = PROPERTY_MEASUREMENT_MESSAGE
        self.label_one = ["Measurement"]
        self.label_two = ["Property"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)


