from importing.RelationshipExtraction.relationshipExtractor import relationshipExtractor
from importing.RelationshipExtraction.schema import HasPropertyRelationships
from importing.utils.openai import chat_with_gpt4


class hasPropertyExtractor(relationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        self.conversation = []
        self.schema = HasPropertyRelationships
        super().__init__(*args, **kwargs)

    def revise_property_connectedness(self):
        """ Validate if all properties are connected to the graph. """
        if self.not_all_properties_connected:
            prompt = f"""- The following property nodes are not connected: {self.node_label_two_ids} \n \n Only return the revised list"""
            response = chat_with_gpt4(self.conversation, prompt)
            self.conversation[-1]["content"] = response



    def generate_result(self):
        """ Generate the final result. """
        return [
            {
                "rel_type": triple[1].upper(),
                "connection": [triple[0], triple[2]]
            }
            for triple in self.triples
        ]

    def refine_results(self):
        self.revise_triples()
        self.revise_property_connectedness()

