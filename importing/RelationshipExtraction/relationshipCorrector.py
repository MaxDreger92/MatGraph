import os

from langchain.chains.conversation.base import ConversationChain
from langchain.chains.ernie_functions import create_structured_output_runnable
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from importing.RelationshipExtraction.input_generator import prepare_lists
from importing.RelationshipExtraction.relationshipValidator import hasParameterValidator, hasPropertyValidator, \
    hasMeasurementValidator, hasManufacturingValidator
from importing.RelationshipExtraction.schema import HasMeasurementRelationships, HasManufacturingRelationships, \
    HasPropertyRelationships, HasParameterRelationships
from importing.RelationshipExtraction.setupMessages import PROPERTY_MEASUREMENT_CORRECTION_MESSAGE, \
    HAS_PROPERTY_CORRECTION_MESSAGE, HAS_PARAMETER_CORRECTION_MESSAGE, MATTER_MANUFACTURING_CORRECTION_MESSAGE, \
    MATTER_MANUFACTURING_MESSAGE, PROPERTY_MEASUREMENT_MESSAGE, MATTER_PROPERTY_MESSAGE, HAS_PARAMETER_MESSAGE


class relationshipCorrector:
    def __init__(self, nodes, graph, query):
        self.query = query
        self._rel_type = None
        self._label_one = None
        self._label_two = None
        self.prompts = []
        self.validator = None
        self.schema = None
        self.setup_message = None
        self.graph = graph
        self.correction_functions = {
            "cardinality": self.cardinality_prompt,
            "triples_correct": self.triples_prompt,
            "no_isolated_nodes_node_list": self.isolated_nodes_prompt,
            "no_cycles": self.cycle_prompt,
            "triples_correct_reversed": self.triples_prompt,
            "no_isolated_nodes": self.isolated_nodes_prompt
        }
        self.nodes = nodes
        self._corrected_graph = graph



    def request_corrections(self, prompts):
        """Extract the relationships using the initial prompt."""
        llm = ChatOpenAI(model_name="gpt-4-1106-preview", openai_api_key=os.environ.get("OPENAI_API_KEY"))
        setup_message = self.setup_message
        setup_message = [*setup_message, *[("ai", self.llm_output), ("human", "Plesae correct the following inconsistencies: {inconsistencies}")]]
        prompt = ChatPromptTemplate.from_messages(setup_message)
        chain = create_structured_output_runnable(self.schema, llm, prompt).with_config(
            {"run_name": f"{self.schema}-correction"})
        self._corrected_graph = chain.invoke({
            "inconsistencies": (', ').join(prompts),
            "input": self.query})
        print("corrected graph", self._corrected_graph)

    def run(self):
        self.full_validate()
        self.generate_prompts()
        print("graph, and prompt", self.corrected_graph, self.prompts)
        if len(self.prompts) > 0:
            self.request_corrections(self.prompts)
        print("graph, and prompt", self.corrected_graph, self.prompts)
        return self.corrected_graph

    def generate_prompts(self):
        self.prompts = []
        for key, value in self.validation_results.items():
            if value != True:
                prompt = self.correction_functions[key](value)
                self.prompts.append(prompt)

    def full_validate(self):
        self._validation_results = self.validator.run()

    def cardinality_prompt(self, input):
        wrong_nodes = input['nodes']
        check_type = input['check_type']
        cardinality = input['cardinality']
        rel_type = input['rel_type']
        node_type = input['node_type']

        # Mapping the check_type to a more human-readable format
        comparison_phrases = {
            '>': 'more than',
            '<': 'less than',
            '!=': 'not exactly'
        }
        comparison_phrase = comparison_phrases.get(check_type, 'an invalid comparison')

        # Constructing a detailed description of the nodes that violate the cardinality constraints
        nodes_description = '; '.join(
            [f"Node '{node}' with related nodes [{','.join(edges)}]" for node, edges in wrong_nodes.items()]).replace("; ", "\n")

        # Assembling the full prompt
        prompt = (
            f"""The following {node_type} nodes have {comparison_phrase} {cardinality} '{rel_type}' relationships, which does not meet the expected cardinality constraints: {nodes_description}."""
        )

        return prompt

    def triples_prompt(self, value):
        issues = []
        wrong_first_nodes = value['wrong_first_nodes']
        rel_type = value['rel_type']
        wrong_second_nodes = value['wrong_second_nodes']
        if wrong_first_nodes:
            issues.append(
                f"The following nodes were incorrectly used as source nodes '{rel_type}' relationship: {', '.join(wrong_first_nodes)}")
        if wrong_second_nodes:
            issues.append(
                f"The following nodes were incorrectly used as target nodes for the '{rel_type}' relationship: {', '.join(wrong_second_nodes)}")
        prompt = (
            f"{'; '.join(issues)}. "
        ).replace("; ", "\n")
        return prompt

    def isolated_nodes_prompt(self, isolated_nodes):
        prompt = f"The following nodes should not be isolated: {', '.join(isolated_nodes)}, connect them via '{self.rel_type}' to the correct nodes."
        return prompt

    def full_connectivity_prompt(self):
        return "The graph is not fully connected. Please ensure that all nodes are connected in a meaningful way."

    def cycle_prompt(self, cycle_check_result):

        # Extract details from the result
        rel1, rel2, problematic_nodes = cycle_check_result['rel1'], cycle_check_result['rel2'], cycle_check_result[
            'nodes']

        # If there are problematic nodes found
        nodes_list_str = ', '.join(problematic_nodes)
        prompt = (
            f"The following nodes have reciprocal relationships involving '{rel1}' and '{rel2}' that may lead to cycles: {nodes_list_str}. "
        )
        return prompt

    @property
    def node_list_one(self):
        return self._label_one_nodes

    @property
    def node_list_two(self):
        return self._label_two_nodes

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
    @property
    def corrected_graph(self):
        return self._corrected_graph

    @property
    def llm_output(self):
        relationships = []
        for item in self.graph.relationships:
            relationships.append(
                {
                    'rel_type': item.type,
                    'connection': [str(item.source), str(item.target)]
                }
            )
        return str({'output': relationships}).replace('{', '{{').replace('}', '}}')


class hasParameterCorrector(relationshipCorrector):
    def __init__(self, nodes, graph, query, *args, **kwargs):
        super().__init__(nodes, graph, query, *args, **kwargs)
        self._rel_type = 'has_parameter'
        self._label_one = ['manufacturing', 'measurement']
        self._label_two = ['parameter']
        self.validator = hasParameterValidator(nodes, graph)
        self.setup_message = HAS_PARAMETER_MESSAGE
        self._label_one_nodes, self._label_two_nodes = prepare_lists(nodes, self.label_one, self.label_two)
        self.schema = HasParameterRelationships


class hasPropertyCorrector(relationshipCorrector):
    def __init__(self, nodes, graph, query, *args, **kwargs):
        super().__init__(nodes, graph, query, *args, **kwargs)
        self._rel_type = 'has_property'
        self._label_one = ['matter']
        self._label_two = ['property']
        self.validator = hasPropertyValidator(nodes, graph)
        self.setup_message = MATTER_PROPERTY_MESSAGE
        self._label_one_nodes, self._label_two_nodes = prepare_lists(nodes, self.label_one, self.label_two)
        self.schema = HasPropertyRelationships


class hasMeasurementCorrector(relationshipCorrector):
    def __init__(self, nodes, graph, query, *args, **kwargs):
        super().__init__(nodes, graph, query, *args, **kwargs)
        self._rel_type = 'has_measurement'
        self._label_one = ['measurement']
        self._label_two = ['property']
        self.validator = hasMeasurementValidator(nodes, graph)
        self.setup_message = PROPERTY_MEASUREMENT_MESSAGE
        self._label_one_nodes, self._label_two_nodes = prepare_lists(nodes, self.label_one, self.label_two)
        self.schema = HasMeasurementRelationships


class hasManufacturingCorrector(relationshipCorrector):
    def __init__(self, nodes, graph, query, *args, **kwargs):
        super().__init__(nodes, graph, query, *args, **kwargs)
        self._rel_type = 'has_manufacturing_nodes'
        self._label_one = ['manufacturing']
        self._label_two = ['matter']
        self.validator = hasManufacturingValidator(nodes, graph)
        self.setup_message = MATTER_MANUFACTURING_MESSAGE
        self._label_one_nodes, self._label_two_nodes = prepare_lists(nodes, self.label_one, self.label_two)
        self.schema = HasManufacturingRelationships
