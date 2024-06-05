import os

from langchain.chains.structured_output import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from graphutils.config import CHAT_GPT_MODEL
from importing.NodeExtraction.nodeValidator import MatterValidator, PropertyValidator, ParameterValidator, \
    ManufacturingValidator, MeasurementValidator, MetadataValidator, SimulationValidator
from importing.NodeExtraction.schema import MatterNodeList, PropertyNodeList, ParameterNodeList, ManufacturingNodeList, \
    MeasurementNodeList, MetadataNodeList
from importing.NodeExtraction.setupMessages import MATTER_AGGREGATION_MESSAGE, PROPERTY_AGGREGATION_MESSAGE, \
    PARAMETER_AGGREGATION_MESSAGE, MANUFACTURING_AGGREGATION_MESSAGE, MEASUREMENT_AGGREGATION_MESSAGE, \
    METADATA_AGGREGATION_MESSAGE


class NodeCorrector:
    def __init__(self, input, output, query):
        self.nodes = output
        self.raw_data = input
        self.query = query
        self._node_type = None
        self.prompts = []
        self.validator = None
        self.schema = None
        self.setup_message = None
        self.correction_functions = {
            "check_indices": self.indices_prompt,
            "check_duplicates": self.duplicates_prompt,
            "check_for_unused_indices": self.unused_indices_prompt,
            "check_invalid_references": self.invalid_references_prompt
        }
        self._corrected_nodes = output

    def invalid_references_prompt(self, nodes):
        return f"The following AttributeReferences do not correspond to existing ColumnIndices: {', '.join(nodes)}\n"

    def unused_indices_prompt(self, nodes):
        prompt = f"You did not extract the data from the following table columns: {', '.join(nodes)}\n"
        return prompt

    def indices_prompt(self, nodes):
        prompt =[]
        for node in nodes:
            if node['value'][0] != node['value'][1]:
                prompt.append(f"The ColumnIndex '{node['index']}' corresponds to the following table-cell value: '{node['value'][1]}', but you assigned the following attribute value to it '{node['value'][0]}'\n")
            if node['type'][0] != node['type'][1]:
                prompt.append(f"The ColumnIndex '{node['index']}' corresponds to the following attribute-type: '{node['type'][1]}', but you assigned the following attribute type to it '{node['type'][0]}'\n")
        prompt = "".join(prompt)
        return prompt

    def duplicates_prompt(self, nodes):
        return f"The following ColumnIndices have been assigned to attributes in more than on node: {', '.join(nodes)}\n"

    def request_corrections(self, prompts):
        """Extract the relationships using the initial prompt."""
        llm = ChatOpenAI(model_name=CHAT_GPT_MODEL, openai_api_key=os.environ.get("OPENAI_API_KEY"))
        setup_message = self.setup_message
        setup_message = [*setup_message, *[("ai", self.llm_output), (
            "human", "Please correct the following inconsistencies: {inconsistencies} \n \nReturn a revised list of nodes that follows the requested format!")]]
        prompt = ChatPromptTemplate.from_messages(setup_message)
        print("Prompt:")
        print(self.query)
        print(self.llm_output)
        print(''.join(prompts))
        chain = create_structured_output_runnable(self.schema, llm, prompt).with_config(
            {"run_name": f"{self.schema}-correction"})
        self._corrected_nodes = chain.invoke({
            "inconsistencies": ('').join(prompts),
            "input": self.query})


    def run(self):
        self.full_validate()
        self.generate_prompts()
        if len(self.prompts) > 0:
            self.request_corrections(self.prompts)
        return self.corrected_nodes

    def generate_prompts(self):
        self.prompts = []
        for key, value in self.validation_results.items():
            if len(value) != 0:
                prompt = self.correction_functions[key](value)
                self.prompts.append(prompt)

    def full_validate(self):
        self._validation_results = self.validator.run()

    @property
    def validation_results(self):
        return self._validation_results

    @property
    def llm_output(self):
        return str({"output": self.nodes.to_dict()}).replace("'", '"').replace('{', '{{').replace('}', '}}')

    @property
    def corrected_nodes(self):
        return self._corrected_nodes


class MatterCorrector(NodeCorrector):
    def __init__(self, input, nodes, query, *args, **kwargs):
        super().__init__(input, nodes, query, *args, **kwargs)
        self.validator = MatterValidator(input, nodes)
        self.setup_message = MATTER_AGGREGATION_MESSAGE
        self.schema = MatterNodeList

class PropertyCorrector(NodeCorrector):
    def __init__(self, input, nodes, query, *args, **kwargs):
        super().__init__(input, nodes, query, *args, **kwargs)
        self.validator = PropertyValidator(input, nodes)
        self.setup_message = PROPERTY_AGGREGATION_MESSAGE
        self.schema = PropertyNodeList

class ParameterCorrector(NodeCorrector):
    def __init__(self, input, nodes, query, *args, **kwargs):
        super().__init__(input, nodes, query, *args, **kwargs)
        self.validator = ParameterValidator(input, nodes)
        self.setup_message = PARAMETER_AGGREGATION_MESSAGE
        self.schema = ParameterNodeList

class ManufacturingCorrector(NodeCorrector):
    def __init__(self, input, nodes, query, *args, **kwargs):
        super().__init__(input, nodes, query, *args, **kwargs)
        self.validator = ManufacturingValidator(input, nodes)
        self.setup_message = MANUFACTURING_AGGREGATION_MESSAGE
        self.schema = ManufacturingNodeList

class MeasurementCorrector(NodeCorrector):
    def __init__(self, input, nodes, query, *args, **kwargs):
        super().__init__(input, nodes, query, *args, **kwargs)
        self.validator = MeasurementValidator(input, nodes)
        self.setup_message = MEASUREMENT_AGGREGATION_MESSAGE
        self.schema = MeasurementNodeList



class MetadataCorrector(NodeCorrector):
    def __init__(self, input, nodes, query, *args, **kwargs):
        super().__init__(input, nodes, query, *args, **kwargs)
        self.validator = MetadataValidator(input, nodes)
        self.setup_message = METADATA_AGGREGATION_MESSAGE
        self.schema = MetadataNodeList

# class SimulationCorrector(NodeCorrector):
#     def __init__(self, input, nodes, query, *args, **kwargs):
#         super().__init__(input, nodes, query, *args, **kwargs)
#         self.validator = SimulationValidator(input, nodes)
#         self.setup_message = SIMULATION_AGGREGATION_MESSAGE
#         self.schema = SimulationNodeList