from importing.RelationshipExtraction.relationshipExtractor import RelationshipExtractor
from importing.utils.openai import chat_with_gpt4


class hasParameterExtractor(RelationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        self.conversation = []
        super().__init__(*args, **kwargs)


    def revise_has_parameter(self):
        wrong_nodes =self.check_one_to_one_destination("has_parameter")
        if wrong_nodes:
            print(f"""These parameter nodes are assigned to multiple measurements/manufacturing nodes: {wrong_nodes}""")
            prompt = f"""- These property nodes have multiple "has_output" edges two different measurement nodes this result 
            does not follow the rules we defined. Please find another solution following the rules: 
            {wrong_nodes} \n \n Only return the revised list"""
            response = chat_with_gpt4(self.api_key, self.conversation, prompt)
            self.update_triples(response)
            print(response)
            self.conversation[-1]["content"] = response

    @property
    def all_parameter_connected(self):
        # Extract the last part of each triple
        last_elements = [triple[0] for triple in self.triples]
        isolated_property_nodes = [node for node in self.node_label_one_ids if node not in last_elements]
        # Check if all elements are present in the last_elements list
        return isolated_property_nodes



    def revise_parameter_connectedness(self):
        """ Validate if all properties are connected to the graph. """
        isolated_parameter_nodes = self.all_parameter_connected
        if len(isolated_parameter_nodes) != 0:
            print(f"The following parameter nodes are not connected: {isolated_parameter_nodes}")
            prompt = f"""- The following parameter nodes are not connected: {isolated_parameter_nodes} \n \n 
            Please connect all parameter nodes in a following the rules i gave you!
            Only return the revised list"""
            response = chat_with_gpt4(self.api_key, self.conversation, prompt)
            print(response)
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