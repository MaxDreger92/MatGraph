from importing.RelationshipExtraction.relationshipExtractor import relationshipExtractor
from importing.RelationshipExtraction.schema import HasParameterRelationships
from importing.utils.openai import chat_with_gpt4


class hasParameterExtractor(relationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        self.conversation = []
        self.schema = HasParameterRelationships
        super().__init__(*args, **kwargs)


    def revise_has_parameter(self):
        wrong_nodes =self.check_one_to_one_destination("has_parameter")
        if wrong_nodes:
            prompt = f"""- These property nodes have multiple "has_output" edges two different measurement nodes this result 
            does not follow the rules we defined. Please find another solution following the rules: 
            {wrong_nodes} \n \n Only return the revised list"""
            response = chat_with_gpt4(self.conversation, prompt)
            self.update_triples(response)
            self.conversation[-1]["content"] = response



    def revise_parameter_connectedness(self):
        """ Validate if all properties are connected to the graph. """
        isolated_parameter_nodes = self.all_parameter_connected
        if len(isolated_parameter_nodes) != 0:
            prompt = f"""- The following parameter nodes are not connected: {isolated_parameter_nodes} \n \n 
            Please connect all parameter nodes in a following the rules i gave you!
            Only return the revised list"""
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
        self.revise_parameter_connectedness()
        self.revise_has_parameter()