import ast
import os

from langchain.chains.structured_output import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from importing.RelationshipExtraction.input_generator import prepare_lists
from importing.utils.openai import chat_with_gpt4


class relationshipExtractor:
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

    @property
    def first_prompt(self):
        """Return the first prompt."""
        return self.prompt

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
        chain = create_structured_output_runnable(
            self.schema,
            llm,
            prompt,
        ).with_config(
            {"run_name": f"{self.schema}-extraction"})
        self.intermediate = chain.invoke({"input": query})
        print(f'Intermediate of {self.schema}: {self.intermediate}')
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
