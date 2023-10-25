from importing.RelationshipExtraction.relationshipExtractor import RelationshipExtractor
from importing.utils.openai import chat_with_gpt4


class hasMeasurementExtractor(RelationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        self.conversation = []
        super().__init__(*args, **kwargs)



    def revise_has_output(self):
        if self.check_one_to_one_destination("has_measurement_output"):
            print(f"""These property nodes are output of multiple measurements: {self.check_one_to_one_destination("has_measurement_output")}""")
            prompt = f"""- These property nodes have multiple "has_output" edges two different measurement nodes this result 
            does not follow the rules we defined. Please find another solution following the rules: 
            {self.check_one_to_one_destination("has_measurement_output")} \n \n Only return the revised list"""
            response = chat_with_gpt4(self.api_key, self.conversation, prompt)
            self.update_triples(response)
            print(response)
            self.conversation[-1]["content"] = response




    def refine_results(self):
        """ Validate the extracted relationships. """
        self.revise_triples()
        self.revise_has_output()
        self.revise_connectedness()