import networkx as nx

from importing.RelationshipExtraction.relationshipExtractor import relationshipExtractor
from importing.RelationshipExtraction.schema import HasManufacturingRelationships
from importing.utils.openai import chat_with_gpt4


class hasManufacturingExtractor(relationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        self.conversation = []
        self.schema = HasManufacturingRelationships
        super().__init__(*args, **kwargs)


    def refine_results(self):
        """ Validate the extracted relationships. """
        self.revise_triples()
        self.revise_manufacturing_cycles()
        self.revise_has_output()
        # self.revise_isolated_nodes()
        self.revise_connectedness()


    def generate_result(self):
        """ Generate the final result. """
        return [
            {
                "rel_type": triple[1].upper(),
                "connection": [triple[0], triple[2]]
            }
            for triple in self.triples
        ]



