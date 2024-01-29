from importing.RelationshipExtraction.relationshipExtractor import RelationshipExtractor
from importing.utils.openai import chat_with_gpt4


class hasPropertyExtractor(RelationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        self.conversation = []
        super().__init__(*args, **kwargs)

    @property
    def not_all_properties_connected(self):
        # Extract the last part of each triple
        last_elements = [triple[2] for triple in self.triples]
        isolated_property_nodes = all(element in last_elements for element in self.node_label_two_ids)
        # Check if all elements are present in the last_elements list
        return isolated_property_nodes

    def revise_property_connectedness(self):
        """ Validate if all properties are connected to the graph. """
        if self.not_all_properties_connected:
            prompt = f"""- The following property nodes are not connected: {self.node_label_two_ids} \n \n Only return the revised list"""
            response = chat_with_gpt4(self.api_key, self.conversation, prompt)
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

