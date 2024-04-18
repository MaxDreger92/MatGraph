import os

from langchain.chains.structured_output import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI

from importing.RelationshipExtraction.examples import (
    MATTER_MANUFACTURING_EXAMPLES,
    HAS_PARAMETER_EXAMPLES,
    MATTER_PROPERTY_EXAMPLES,
)
from importing.RelationshipExtraction.input_generator import prepare_lists
from importing.RelationshipExtraction.schema import (
    HasManufacturingRelationships,
    HasMeasurementRelationships,
    HasParameterRelationships,
    HasPropertyRelationships,
)
from importing.RelationshipExtraction.setupMessages import (
    MATTER_MANUFACTURING_MESSAGE,
    PROPERTY_MEASUREMENT_MESSAGE,
    HAS_PARAMETER_MESSAGE,
    MATTER_PROPERTY_MESSAGE,
)


class spRelationshipExtractor:
    """
    Base class for extracting relationships from structured data.

    Attributes:
        input_json (dict): Input data in JSON format.
        context (str): Context in which relationships are to be extracted.
        setup_message (str): Initial setup message for conversation.
    """

    def __init__(self, input_json, context):
        """
        Initializes the RelationshipExtractor with input data and context.
        """
        self.input_json = input_json
        self.context = context
        self.setup_message = None
        self.triples = []
        self.conversation = None
        self.prompt = ""
        self._results = None

    @property
    def label_one_nodes(self):
        """Returns nodes associated with the first label."""
        return self._label_one_nodes

    @property
    def label_two_nodes(self):
        """Returns nodes associated with the second label."""
        return self._label_two_nodes

    @property
    def first_prompt(self):
        """Returns the first prompt used for extraction."""
        return self.prompt

    def create_query(self):
        """Generates the initial query prompt for relationship extraction."""
        prompt = f"{', '.join(self.label_one)}: {self.label_one_nodes} \n{', '.join(self.label_two)}: {self.label_two_nodes} \nContext: {self.context}"
        return prompt

    def initial_extraction(self):
        """Performs the initial extraction of relationships using GPT-4."""
        query = self.create_query()
        llm = ChatOpenAI(model_name="gpt-4-1106-preview", openai_api_key=os.getenv("OPENAI_API_KEY"))
        setup_message = self.setup_message
        prompt = ChatPromptTemplate.from_messages(setup_message)

        if self.examples:
            example_prompt = ChatPromptTemplate.from_messages([('human', "{input}"), ('ai', "{output}")])
            few_shot_prompt = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=self.examples)
            prompt = ChatPromptTemplate.from_messages([setup_message[0], few_shot_prompt, *setup_message[1:]])

        chain = create_structured_output_runnable(self.schema, llm, prompt).with_config(
            {"run_name": f"{self.schema}-extraction"})
        self.intermediate = chain.invoke({"input": query})
        self.generate_result()

    def run(self):
        """Executes the relationship extraction process."""
        if not self.label_two_nodes or not self.label_one_nodes:
            return []
        self.initial_extraction()
        return self._results

    def generate_result(self):
        """Generates the final result of the extraction process."""
        self._results = {
            "graph": self.intermediate,
            'nodes': self.input_json,
            'query': self.create_query(),
        }

    @property
    def results(self):
        """Returns the results of the extraction."""
        return self._results


class HasManufacturingExtractor(RelationshipExtractor):
    """Extractor for Matter-Manufacturing relationships."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = HasManufacturingRelationships
        self.setup_message = MATTER_MANUFACTURING_MESSAGE
        self.label_one = ["matter"]
        self.label_two = ["manufacturing"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)
        self.examples = MATTER_MANUFACTURING_EXAMPLES


class HasMeasurementExtractor(RelationshipExtractor):
    """Extractor for Measurement-Property relationships."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = HasMeasurementRelationships
        self.setup_message = PROPERTY_MEASUREMENT_MESSAGE
        self.label_one = ["Measurement"]
        self.label_two = ["Property"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)


class HasParameterExtractor(RelationshipExtractor):
    """Extractor for relationships between Manufacturing or Measurement and Parameters."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = HasParameterRelationships
        self.setup_message = HAS_PARAMETER_MESSAGE
        self.label_one = ["manufacturing", "measurement"]
        self.label_two = ["parameter"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)
        self.examples = HAS_PARAMETER_EXAMPLES


class HasPropertyExtractor(RelationshipExtractor):
    """Extractor for Matter-Property relationships."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = HasPropertyRelationships
        self.setup_message = MATTER_PROPERTY_MESSAGE
        self.label_one = ["matter"]
        self.label_two = ["property"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)
        self.examples = MATTER_PROPERTY_EXAMPLES
