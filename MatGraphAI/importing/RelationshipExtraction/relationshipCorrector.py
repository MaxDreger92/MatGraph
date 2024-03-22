import os

from langchain.chains.conversation.base import ConversationChain
from langchain.chains.ernie_functions import create_structured_output_runnable
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class relationshipCorrector:
    def __init__(self, rel_type, label_one, label_two, validator, conversation, results):
        self._rel_type = rel_type
        self._label_one = label_one
        self._label_two = label_two
        self.prompts = []
        self.validator = validator
        self.schema = None
        self.results = results
        self.correction_functions = {
            "cardinality_one_target": self.revise_cardinality,
            "triples_correct": self.revise_triples,
            "correct_no_isolated_nodes_node_list": self.revise_isolated_nodes,
            "no_cycles": self.revise_cycles,
            "triples_correct_reversed": self.revise_triples,
            "no_isolated_nodes": self.revise_isolated_nodes
        }
        self.conversation = conversation


    def request_correction(self, query):
        """Extract the relationships using the initial prompt."""
        llm = ChatOpenAI(model_name="gpt-4-1106-preview", openai_api_key=os.environ.get("OPENAI_API_KEY"))
        setup_message = self.conversation
        prompt = ChatPromptTemplate.from_messages(setup_message)
        prompt.append(("human", query))
        conversation = ConversationChain(
            prompt=prompt,
            llm=llm,
            verbose=True,
            memory=ConversationBufferMemory(),
        )
        chain = create_structured_output_runnable(self.schema, llm, conversation).with_config(
            {"run_name": f"{self.schema}-correction"})
        self.intermediate = chain.invoke()



    def full_validate(self):
        self.validation_results = self.validator.validate()

    def create_cardinality_prompt(self, value):
            return f"""The nodes: {','.join(value)} should have only a {self.rel_type} single edge to other nodes. Please correct the results following the given format"""


    def revise_cardinality_one_target(self, cardinality, rel_type):
        if self.validator.validate_cardinality(cardinality, rel_type):
            return True
        else:
            query = self.create_cardinality_prompt(self.validator.validate_cardinality(cardinality, rel_type))
            self.request_correction(query)


    def revise_triples(self, value):
        if value == 0:
            return f"""- The triples are not correct. Please correct this."""
        else:
            return f"""- The triples are not correct. Please correct this."""

    def revise_isolated_nodes(self, value):
        if value == 0:
            return f"""- There are isolated nodes in the list of {self.label_two}. Please correct this."""
        else:
            return f"""- There are isolated nodes in the list of {self.label_two}. Please correct this."""

    def revise_cycles(self, value):
        if value == 0:
            return f"""- There are cycles in the graph. Please correct this."""
        else:
            return f"""- There are cycles in the graph. Please correct this."""

    def revise_triples(self, value):
        if value == 0:
            return f"""- The triples are not correct. Please correct this."""
        else:
            return f"""- The triples are not correct. Please correct this."""

    def revise_isolated_nodes(self, value):
        if value == 0:
            return f"""- There are isolated nodes in the list of {self.label_two}. Please correct this."""
        else:
            return f"""- There are isolated nodes in the list of {self.label_two}. Please correct this."""


    @property
    def validation_results(self):
        return self._validation_results

    @property
    def rel_type(self):
        return self._rel_type

    @property
    def label_one(self):
        return self._label_one

    @property
    def label_two(self):
        return self._label_two

    def generate_prompts(self):
        for key, value in self.validation_results.items():
            if value != True:
                self.prompts.append(self.correction_functions[key](value))



    def revise_has_output(self):
        if self.check_one_to_one_destination("has_output"):
            prompt = f"""- These matter have multiple "has_output" edges two different manufacturing nodes this result 
            does not follow the rules we defined. Please find another solution following the rules: 
            {self.check_one_to_one_destination("has_output")} \n \n Only return the revised list"""
            response = chat_with_gpt4(self.conversation, prompt)
            self.update_triples(response)
            self.update_triples(response)
            self.conversation.append({"role": "user", "content": prompt})
            self.conversation.append({"role": "assistant", "content": response})


    def revise_manufacturing_cycles(self):
        if self.manufacturing_cycles:
            prompt = f"""- The following matter nodes share 'is_input' and 'has_output' edges with one and the same 
                manufacturing nodes: {self.manufacturing_cycles}. 
                Suggest another reasonable solution in which matter nodes share do not share 'is_input' and 'has_output' 
                edges with one and the same manufacturing node. 
                \n \n Only return the revised list"""
            response = chat_with_gpt4(self.conversation, prompt)
            self.update_triples(response)
            self.conversation.append({"role": "user", "content": prompt})
            self.conversation.append({"role": "assistant", "content": response})
            self.revise_manufacturing_cycles()
