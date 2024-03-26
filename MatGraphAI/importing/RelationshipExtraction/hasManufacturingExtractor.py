from importing.RelationshipExtraction.examples import MATTER_MANUFACTURING_EXAMPLES
from importing.RelationshipExtraction.input_generator import prepare_lists
from importing.RelationshipExtraction.relationshipExtractor import relationshipExtractor
from importing.RelationshipExtraction.schema import HasManufacturingRelationships
from importing.RelationshipExtraction.setupMessages import MATTER_MANUFACTURING_MESSAGE


class hasManufacturingExtractor(relationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation = []
        self.schema = HasManufacturingRelationships
        self.setup_message = MATTER_MANUFACTURING_MESSAGE
        self.rel_type = "is_manufacturing_input"
        self.rel_type2 = "has_manufacturing_output"
        self.label_one = ["matter"]
        self.label_two = ["manufacturing"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)
        self.examples = MATTER_MANUFACTURING_EXAMPLES








