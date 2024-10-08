import os

from langchain.chains.structured_output import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_fixed

from graphutils.config import CHAT_GPT_MODEL
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
    HasPropertyRelationships, HasPartMatterRelationships, HasPartManufacturingRelationships,
    HasPartMeasurementRelationships, HasMetadataRelationships,
)
from importing.RelationshipExtraction.setupMessages import (
    MATTER_MANUFACTURING_MESSAGE,
    PROPERTY_MEASUREMENT_MESSAGE,
    HAS_PARAMETER_MESSAGE,
    MATTER_PROPERTY_MESSAGE, MATTER_MATTER_MESSAGE, MEASUREMENT_MEASUREMENT_MESSAGE,
    MANUFACTURING_MANUFACTURING_MESSAGE, PROCESS_METADATA_MESSAGE,
)


class RelationshipExtractor:
    """
    Base class for extracting relationships from structured data.

    Attributes:
        input_json (dict): Input data in JSON format.
        context (str): Context in which relationships are to be extracted.
        setup_message (str): Initial setup message for conversation.
    """

    def __init__(self, input_json, context, header, first_line, *args, **kwargs):
        """
        Initializes the RelationshipExtractor with input data and context.
        """
        self.header = header
        self.first_line = first_line
        self.input_json = input_json
        self.context = context
        self.setup_message = None
        self.triples = []
        self.conversation = None
        self.prompt = ""
        self._results = None
        self.examples = None

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
        label_one_nodes = [
            {
                "node_id": node['id'],
                "table_position": [
                    attr['index']
                    for attribute_type in node['attributes'].values()
                    for attr in (attribute_type if isinstance(attribute_type, list) else [attribute_type])
                    if 'index' in attr and attr['index'] not in ['inferred', 'missing']
                ],
                "node_attributes": {
                    key: [val['value'] for val in (value_list if isinstance(value_list, list) else [value_list])]
                    for key, value_list in node["attributes"].items()
                }

            }
            for node in self.label_one_nodes
        ]
        label_two_nodes = [
            {
                "node_id": node['id'],
                "table_position": [
                    attr['index']
                    for attribute_type in node['attributes'].values()
                    for attr in (attribute_type if isinstance(attribute_type, list) else [attribute_type])
                    if 'index' in attr and attr['index'] not in ['inferred', 'missing']
                ],
                "node_attributes": {
                    key: [val['value'] for val in (value_list if isinstance(value_list, list) else [value_list])]
                    for key, value_list in node["attributes"].items()
                }

            }
            for node in self.label_two_nodes
        ]
        prompt = f"""
Scientific Context: {self.context}
{', '.join(self.label_one)} nodes: {label_one_nodes}
{', '.join(self.label_two)} nodes: {label_two_nodes}
 
 Table Header: {', '.join(self.header)}
 First Row: {', '.join(self.first_line)}"""
        print(prompt)
        return prompt

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def initial_extraction(self):
        """Performs the initial extraction of relationships using GPT-4."""
        query = self.create_query()
        llm = ChatOpenAI(model_name=CHAT_GPT_MODEL, openai_api_key=os.getenv("OPENAI_API_KEY"))
        setup_message = self.setup_message
        prompt = ChatPromptTemplate.from_messages(setup_message)

        if self.examples:
            example_prompt = ChatPromptTemplate.from_messages([('human', "{input}"), ('ai', "{output}")])
            few_shot_prompt = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=self.examples)
            prompt = ChatPromptTemplate.from_messages([setup_message[0], few_shot_prompt, *setup_message[1:]])
            print(f"Example Prompt: {prompt}")

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


class HasPartMatterExtractor(RelationshipExtractor):
    """Extractor for Matter-Manufacturing relationships."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = HasPartMatterRelationships
        self.setup_message = MATTER_MATTER_MESSAGE
        self.label_one = ["matter"]
        self.label_two = ["matter"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)

    def create_query(self):
        """Generates the initial query prompt for relationship extraction."""
        label_one_nodes = [{"node_id": node['id'], "node_attributes": node["attributes"]} for node in
                           self.label_one_nodes]
        prompt = f"""
Scientific Context: {self.context}
{', '.join(self.label_one)} nodes: {label_one_nodes}
 
 Table Header: {', '.join(self.header)}
 First Row: {', '.join(self.first_line)}"""
        return prompt


class HasPartManufacturingExtractor(RelationshipExtractor):
    """Extractor for Matter-Manufacturing relationships."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = HasPartManufacturingRelationships
        self.setup_message = MANUFACTURING_MANUFACTURING_MESSAGE
        self.label_one = ["manufacturing"]
        self.label_two = ["manufacturing"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)

    def create_query(self):
        """Generates the initial query prompt for relationship extraction."""
        label_one_nodes = [{"node_id": node['id'], "node_attributes": node["attributes"]} for node in
                           self.label_one_nodes]
        prompt = f"""
Scientific Context: {self.context}
{', '.join(self.label_one)} nodes: {label_one_nodes}
 
 Table Header: {', '.join(self.header)}
 First Row: {', '.join(self.first_line)}"""
        print(prompt)
        return prompt


class HasPartMeasurementExtractor(RelationshipExtractor):
    """Extractor for Matter-Manufacturing relationships."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = HasPartMeasurementRelationships
        self.setup_message = MEASUREMENT_MEASUREMENT_MESSAGE
        self.label_one = ["measurement"]
        self.label_two = ["measurement"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)

    def create_query(self):
        """Generates the initial query prompt for relationship extraction."""
        label_one_nodes = [{"node_id": node['id'], "node_attributes": node["attributes"]} for node in
                           self.label_one_nodes]
        prompt = f"""
Scientific Context: {self.context}
{', '.join(self.label_one)} nodes: {label_one_nodes}
 
 Table Header: {', '.join(self.header)}
 First Row: {', '.join(self.first_line)}"""
        print(prompt)
        return prompt


class HasMeasurementExtractor(RelationshipExtractor):
    """Extractor for Measurement-Property relationships."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = HasMeasurementRelationships
        self.setup_message = PROPERTY_MEASUREMENT_MESSAGE
        self.label_one = ["measurement"]
        self.label_two = ["property"]
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


class HasMetadataExtractor(RelationshipExtractor):
    """Extractor for Metadata relationships."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = HasMetadataRelationships
        self.setup_message = PROCESS_METADATA_MESSAGE
        self.label_one = ["manufacturing", "measurement"]
        self.label_two = ["metadata"]
        self._label_one_nodes, self._label_two_nodes = prepare_lists(self.input_json, self.label_one, self.label_two)
