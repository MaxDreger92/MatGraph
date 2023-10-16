import ast
from pprint import pprint

import networkx as nx

from src.RelationshipExtraction.input_generator import csv_to_json, prepare_lists
from src.RelationshipExtraction.setupMessages import MATTER_MANUFACTURING_MESSAGE
from src.utils.openai import chat_with_gpt4


class RelationshipExtractor:
    """
    Base class for extracting relationships from data.

    Attributes:
    - input_json (dict): Input data in JSON format.
    - setup_message (str): Message used for setup.
    - gpt_chat (function): Chat function to communicate with GPT-4.
    - label_one (str): First label for relationships.
    - label_two (str): Second label for relationships.
    - context (str): Context in which relationships are to be extracted.
    """

    def __init__(self, input_json, setup_message, gpt_chat, label_one, label_two, context):
        self.input_json = input_json
        self.setup_message = setup_message
        self.gpt_chat = gpt_chat
        self.context = context
        self.label_one, self.label_two = label_one, label_two
        self.label_one_nodes, self.label_two_nodes = prepare_lists(self.input_json, label_one, label_two)
        self.triples = []
        self.conversation = setup_message
        self.prompt = ""

    def _flatten_relations(self):
        """ Flatten the relationship triples. """
        return [item for sublist in self.triples for item in sublist if isinstance(item, (int, str))]

    @property
    def isolated_nodes(self):
        """ List of nodes that are isolated (not present in relationship triples). """
        flat_relations = self._flatten_relations()
        nodes = [item['node_id'] for item in [*self.label_one_nodes, *self.label_two_nodes]]
        return [node for node in nodes if node not in flat_relations]

    @property
    def is_connected(self):
        """ Check if the relationship graph is connected. """
        g = nx.Graph()
        for triple in self.triples:
            src, _, dst = triple
            g.add_edge(src, dst)
        return nx.is_connected(g)

    def generate_first_prompt(self):
        """ Generate the first prompt for extraction. """
        self.prompt = f"""Again only the list! {{{self.label_one}: {self.label_one_nodes}, 
        {self.label_two}: {self.label_two_nodes}, "Context": {self.context}}}"""

    @property
    def first_prompt(self):
        """ Returns the first prompt. """
        return self.generate_first_prompt()

    def initial_extraction(self):
        """ Extract the relationships using the initial prompt. """
        response = self.gpt_chat(self.setup_message, self.prompt)
        self.triples = ast.literal_eval(response.replace(" ", "").replace("{", "").replace("}", ""))
        self.conversation.append({"role": "user", "content": self.prompt})
        self.conversation.append({"role": "assistant", "content": response})


def refine_results():
    """ Base method for validation. Should be implemented in derived classes. """
    raise NotImplementedError("This method should be implemented by the child class.")


class MatterManufacturingExtractor(RelationshipExtractor):
    """
    Extractor specific to Matter-Manufacturing relationships.

    Attributes:
    - conversation (list): Placeholder for conversation logs with GPT-4.
    """

    def __init__(self, *args, **kwargs):
        self.conversation = []
        super().__init__(*args, **kwargs)

    def validate_has_output(self):
        """Validate if any node has a 'has_output' relationship with more than one node using NetworkX."""

        # Create a directed graph from the triples
        g = nx.DiGraph()
        for src, rel, dst in self.triples:
            g.add_edge(src, dst, relation=rel)
        wrong_nodes = {}

        # Check nodes with 'has_output' relationship for multiple outputs
        for src, dst, data in g.edges(data=True):
            if data['relation'] == 'has_output' and g.in_degree(dst) > 1:
                if dst in wrong_nodes.keys():
                    wrong_nodes[dst].append(src)
                else:
                    wrong_nodes[dst] = [src]

        return wrong_nodes if len(wrong_nodes.keys()) != 0 else False

    def refine_results(self):
        """ Validate the extracted relationships. """
        if self.validate_has_output():
            print(f"These nodes have multiple outputs: {self.validate_has_output()}")
            prompt = f"""- These matter have multiple "has_output" edges two different manufacturing nodes this result 
            does not follow the rules we defined. Please find another solution following the rules: 
            {self.validate_has_output()} \n \n Only return the revised list"""
            response = chat_with_gpt4(self.conversation, prompt)
            print(response)
            self.conversation[-1]["content"] = response
        if len(self.isolated_nodes) != 0:
            print(f"The following nodes are missing: {self.isolated_nodes}")
            prompt = f"""- Some of the nodes are still not connected. Please connect the following nodes following your
            instructions: {", ".join(self.isolated_nodes)} \n \n Only return the revised list"""
            response = chat_with_gpt4(self.conversation, prompt)
            print(response)
            self.conversation[-1]["content"] = response
        if not self.is_connected:
            print("The graph is not connected. Please connect the nodes.")
            prompt = f"""- The graph is not connected. Please connect the nodes. \n \n Only return the revised list"""
            response = chat_with_gpt4(self.conversation, prompt)
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



def main():
    file_name = "../../data/materials.csv"
    print(f"Testing relationship extraction for... \n {file_name} \n \n")
    input_json = (csv_to_json(file_name))
    extractor = MatterManufacturingExtractor(input_json, MATTER_MANUFACTURING_MESSAGE, chat_with_gpt4, "Matter",
                                             "Manufacturing", "Solar Cell fabrication")
    extractor.generate_first_prompt()
    extractor.initial_extraction()
    pprint(extractor.triples, indent=4)
    print(extractor.isolated_nodes)
    print(extractor.is_connected)
    extractor.refine_results()
    # triples = [['10', 'is_input', '3'],
    #            ['3', 'has_output', '2'],
    #            ['2', 'is_input', '14'],
    #            ['20', 'is_input', '14'],
    #            ['47', 'is_input', '14'],
    #            ['23', 'is_input', '14'],
    #            ['25', 'is_input', '14'],
    #            ['14', 'has_output', '13'],
    #            ['13', 'is_input', '27'],
    #            ['33', 'is_input', '27'],
    #            ['27', 'has_output', '26'],
    #            ['26', 'is_input', '37'],
    #            ['43', 'is_input', '37'],
    #            ['37', 'has_output', '36']]
    # print(validate_has_output(triples))
    # if validate_has_output(triples):
    #     print(f"These nodes have multiple outputs: {validate_has_output(triples)}")


if __name__ == "__main__":
    main()
