import ast
import os

import networkx as nx
from langchain.chains.structured_output import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from importing.RelationshipExtraction.input_generator import prepare_lists
from importing.utils.openai import chat_with_gpt4


class RelationshipExtractor:
    """
    Base class for extracting relationships from data.

    Attributes:
        input_json (dict): Input data in JSON format.
        setup_message (str): Message used for setup.
        gpt_chat (function): Chat function to communicate with GPT-4.
        label_one (str): First label for relationships.
        label_two (str): Second label for relationships.
        context (str): Context in which relationships are to be extracted.
    """

    def __init__(self, input_json, setup_message, label_one, label_two, context):
        """
        Initializes the RelationshipExtractor with necessary information.
        """
        self.input_json = input_json
        self.setup_message = setup_message
        self.context = context
        self.label_one, self.label_two = label_one, label_two
        self.label_one_nodes, self.label_two_nodes = prepare_lists(self.input_json, label_one, label_two)
        self.triples = []
        self.conversation = setup_message
        self.prompt = ""

    def check_one_to_one_destination(self, rel):
        """Validate if any node has a 'has_output' relationship with more than one node using NetworkX."""

        # Create a directed graph from the triples
        g = nx.DiGraph()
        for src, rel, dst in self.triples:
            g.add_edge(src, dst, relation=rel)
        wrong_nodes = {}

        # Check nodes with 'has_output' relationship for multiple outputs
        for src, dst, data in g.edges(data=True):
            if data['relation'] == rel and g.in_degree(dst) > 1:
                if dst in wrong_nodes.keys():
                    wrong_nodes[dst].append(src)
                else:
                    wrong_nodes[dst] = [src]
        return wrong_nodes if len(wrong_nodes.keys()) != 0 else False

    @property
    def check_one_to_one_source(self, rel):
        """Validate if any node has a 'has_output' relationship with more than one node using NetworkX."""

        # Create a directed graph from the triples
        g = nx.DiGraph()
        for src, rel, dst in self.triples:
            g.add_edge(src, dst, relation=rel)
        wrong_nodes = {}

        # Check nodes with 'has_output' relationship for multiple outputs
        for src, dst, data in g.edges(data=True):
            if data['relation'] == rel and g.in_degree(src) > 1:
                if dst in wrong_nodes.keys():
                    wrong_nodes[src].append(dst)
                else:
                    wrong_nodes[src] = [dst]
        return wrong_nodes if len(wrong_nodes.keys()) != 0 else False

    @property
    def flatten_relations(self):
        """Flatten the relationship triples."""
        return [item for sublist in self.triples for item in sublist if isinstance(item, (int, str))]

    @property
    def node_ids(self):
        """Get all node IDs from label_one_nodes and label_two_nodes."""
        return [item['id'] for item in [*self.label_one_nodes, *self.label_two_nodes]]

    @property
    def node_label_one_ids(self):
        """Get node IDs from label_one_nodes."""
        return [item['id'] for item in self.label_one_nodes]

    @property
    def node_label_two_ids(self):
        """Get node IDs from label_two_nodes."""
        return [item['id'] for item in self.label_two_nodes]

    @property
    def first_prompt(self):
        """Return the first prompt."""
        return self.prompt

    @property
    def isolated_nodes(self):
        """Get a list of nodes that are isolated (not present in relationship triples)."""
        return [str(node) for node in self.node_ids if node not in self.flatten_relations]

    @property
    def is_connected(self):
        """Check if the relationship graph is connected."""
        g = nx.Graph()
        for triple in self.triples:
            src, _, dst = triple
            g.add_edge(src, dst)
        return nx.is_connected(g)

    @property
    def triples_correct(self):
        """
        Validate the triples to check if they use correct nodes for label_one and label_two.
        """
        wrong_second_nodes = [triple[2] for triple in self.triples if triple[2] not in self.node_label_two_ids]
        wrong_first_nodes = [triple[0] for triple in self.triples if triple[0] not in self.node_label_one_ids]
        return [wrong_first_nodes, wrong_second_nodes]

    def update_triples(self, response):
        """Update the triples based on a response."""
        self.triples = ast.literal_eval(response.replace(" ", "").replace("{", "").replace("}", ""))

    def revise_isolated_nodes(self):
        """Handle isolated nodes and attempt to connect them."""
        if self.isolated_nodes:
            prompt = f"""Some nodes are still not connected. Please connect the following nodes: {", ".join(self.isolated_nodes)}.
            Only return the revised list!"""
            response = chat_with_gpt4(self.conversation, prompt)
            self.update_triples(response)
            self.conversation[-1]["content"] = response

    def revise_triples(self):
        """Revise the triples based on validation results."""
        triples_correct = self.triples_correct

        if len(triples_correct[0]) != 0 or len(triples_correct[1]) != 0:

            prompt = ""
            if self.triples_correct[0]:
                prompt += f"The following nodes are not in the list of {self.label_one}: {self.triples_correct[0]}."
            if self.triples_correct[1]:
                prompt += f"The following {self.label_two} nodes are not in the correct position of the triples: {self.triples_correct[1]}."
            prompt += "Only return the revised list."
            response = chat_with_gpt4(self.conversation, prompt)
            self.update_triples(response)
            self.conversation[-1]["content"] = response

    def revise_connectedness(self):
        """Ensure that the graph is connected."""
        if not self.is_connected:
            prompt = ("""The graph is divided into subgraphs. Please try to connect them to form one graph in a meaningful way. 
                      Return only the revised list.""")
            response = chat_with_gpt4(self.conversation, prompt)
            self.update_triples(response)
            self.conversation[-1]["content"] = response



    def create_query(self):
        """Generate the first prompt for extraction."""
        prompt = f"""Now, only the list! \n {", ".join(self.label_one)}: {self.label_one_nodes}, \n{', '.join(self.label_two)}: {self.label_two_nodes}, \nContext: {self.context}"""
        return prompt

    def initial_extraction(self):
        """Extract the relationships using the initial prompt."""
        query = self.create_query()
        llm = ChatOpenAI(model_name="gpt-4-1106-preview", openai_api_key=os.environ.get("OPENAI_API_KEY"))
        setup_message = self.setup_message
        prompt = ChatPromptTemplate.from_messages(setup_message)
        chain = create_structured_output_runnable(self.schema, llm, prompt).with_config(
            {"run_name": f"{self.schema}-extraction"})
        self.intermediate = chain.invoke({"input": query})
        print(f"Used the following prompt: {query}")
        print(f"Finished extraction for {self.schema} {self.intermediate}")

        return self


    def refine_results(self):
        """Base method for validation. Should be implemented in derived classes."""
        raise NotImplementedError("This method should be implemented by the child class.")

    def run(self):
        """Run the extraction process."""
        if len(self.label_two_nodes) == 0 or len(self.label_one_nodes) == 0:
            return []
        self.initial_extraction()
        self.refine_results()
        return self.generate_result()

    def generate_result(self):
        """ Generate the final result. """
        return [
            {
                "rel_type": triple[1].upper(),
                "connection": [triple[0], triple[2]]
            }
            for triple in self.triples
        ]
















