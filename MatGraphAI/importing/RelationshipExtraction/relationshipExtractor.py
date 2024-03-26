import ast
import os

from langchain.chains.structured_output import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI


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

    def __init__(self, input_json, context):
        """
        Initializes the RelationshipExtractor with necessary information.
        """
        self.input_json = input_json
        self.setup_message = None
        self.context = context
        self.triples = []
        self.conversation = None
        self.prompt = ""

    @property
    def label_one_nodes(self):
        """Get all nodes from label_one_nodes."""
        return self._label_one_nodes

    @property
    def label_two_nodes(self):
        """Get all nodes from label_two_nodes."""
        return self._label_two_nodes

    @property
    def first_prompt(self):
        """Return the first prompt."""
        return self.prompt

    def update_triples(self, response):
        """Update the triples based on a response."""
        self.triples = ast.literal_eval(response.replace(" ", "").replace("{", "").replace("}", ""))

    def create_query(self):
        """Generate the first prompt for extraction."""
        prompt = f"""{", ".join(self.label_one)}: {self.label_one_nodes} \n{', '.join(self.label_two)}: {self.label_two_nodes} \nContext: {self.context}"""
        return prompt

    def initial_extraction(self):
        """Extract the relationships using the initial prompt."""
        query = self.create_query()
        llm = ChatOpenAI(model_name="gpt-4-1106-preview", openai_api_key=os.environ.get("OPENAI_API_KEY"))
        setup_message = self.setup_message
        print(query)
        prompt = ChatPromptTemplate.from_messages(setup_message)
        if self.examples is not None:
            example_prompt = ChatPromptTemplate.from_messages([('human', "{input}"), ('ai', "{output}")])
            few_shot_prompt = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=self.examples)
            prompt = ChatPromptTemplate.from_messages([setup_message[0], few_shot_prompt, *setup_message[1:]])

        chain = create_structured_output_runnable(
            self.schema,
            llm,
            prompt,
        ).with_config(
            {"run_name": f"{self.schema}-extraction"})
        self.intermediate = chain.invoke({"input": query})
        return {"nodes": self.input_json,
                "graph": self.intermediate,
                "query": query,}

    def run(self):
        """Run the extraction process."""
        if len(self.label_two_nodes) == 0 or len(self.label_one_nodes) == 0:
            return []
        self.initial_extraction()
        self.generate_result()
        return self.results

    def generate_result(self):
        """ Generate the final result. """
        self._results = {"graph": self.intermediate,
                         'nodes': self.input_json,
                         'query': self.create_query(),

                         }

    @property
    def results(self):
        return self._results
