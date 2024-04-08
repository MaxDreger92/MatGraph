import os
from collections import defaultdict

from langchain.chains import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.runnables import chain, RunnableParallel
from langchain_openai import ChatOpenAI

from graphutils.general import TableDataTransformer
from importing.NodeExtraction.examples import MATTER_AGGREGATION_EXAMPLES, PARAMETER_AGGREGATION_EXAMPLES, \
    MANUFACTURING_AGGREGATION_EXAMPLES
from importing.NodeExtraction.schema import MatterNodeList, PropertyNodeList, ManufacturingNodeList, \
    MeasurementNodeList, MetadataNodeList, ParameterNodeList
from importing.NodeExtraction.setupMessages import MATTER_AGGREGATION_MESSAGE, PROPERTY_AGGREGATION_MESSAGE, \
    PARAMETER_AGGREGATION_MESSAGE, MANUFACTURING_AGGREGATION_MESSAGE, MEASUREMENT_AGGREGATION_MESSAGE
from importing.models import NodeExtractionReport


class NodeAggregator:
    def __init__(self, data, context, setup_message, additional_context):
        self.header = [f"{element['header']}" for element in data]
        self.attributes = [f"{element['attribute']}/{element['index']}" for element in data]
        self.row = [element['column_values'][0] if element['column_values'] else '' for element in data]
        self.setup_message = setup_message
        self.context = context
        self.additional_context = additional_context
        self.conversation = self.setup_message
        self.label = None
        self.schema = None
        self._intermediate = None

    def create_query(self):
        return f"""
        Context: {self.context}
    
        Attribute/ColumnIndex: {", ".join(self.attributes)}
        Table: {", ".join(self.header)}
        Sample Row: {", ".join(self.row)}
        
        {self.additional_context}
        """

    @property
    def intermediate(self):
        return self._intermediate

    @intermediate.setter
    def intermediate(self, data):
        self._intermediate = data

    def validate(self):
        return self.intermediate

    def aggregate(self):
        """Performs the initial extraction of relationships using GPT-4."""
        print(f"Aggregate {self.schema} nodes")
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
        print(f"Aggregated {self.schema} nodes")
        return self

class MatterAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=MATTER_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "matter"
        self.schema = MatterNodeList
        self.examples = MATTER_AGGREGATION_EXAMPLES


class PropertyAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=PROPERTY_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "property"
        self.schema = PropertyNodeList
        self.examples = None


class ParameterAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=PARAMETER_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "parameter"
        self.schema = ParameterNodeList
        self.examples = PARAMETER_AGGREGATION_EXAMPLES


class ManufacturingAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=MANUFACTURING_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "manufacturing"
        self.schema = ManufacturingNodeList
        self.examples = MANUFACTURING_AGGREGATION_EXAMPLES


class MeasurementAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=MEASUREMENT_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "measurement"
        self.schema = MeasurementNodeList
        self.examples = None


class MetadataAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=PARAMETER_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "metadata"
        self.schema = MetadataNodeList
        self.examples = None


def group_by_prefix(self, data):
    grouped = defaultdict(list)
    for entry in data:
        prefix = entry['header'].split('_', 1)[0]
        grouped[prefix].append(entry)
    return grouped


def get_aggregator(iterable, data_type, aggregator_class, context):
    if data_type in iterable and iterable[data_type]:
        data = iterable[data_type]
        context = context

        grouped_data = group_by_prefix(data) if data_type == "property" else {None: data}
        for entries in grouped_data.values():
            aggregator = aggregator_class(entries, context)
            return aggregator


def aggregate_nodes(data, type, aggregator_class):
    if aggregator := get_aggregator(data['input'], type, aggregator_class, data['context']):
        return aggregator.aggregate()
    return


@chain
def aggregate_properties(data):
    return aggregate_nodes(data, "Property", PropertyAggregator)


@chain
def aggregate_parameters(data):
    return aggregate_nodes(data, "Parameter", ParameterAggregator)


@chain
def aggregate_manufacturing(data):
    return aggregate_nodes(data, "Manufacturing", ManufacturingAggregator)


@chain
def aggregate_measurement(data):
    return aggregate_nodes(data, "Measurement", MeasurementAggregator)


@chain
def aggregate_metadata(data):
    return aggregate_nodes(data, "Metadata", MetadataAggregator)


@chain
def aggregate_matters(data):
    return aggregate_nodes(data, "Matter", MatterAggregator)


@chain
def validate_matters(aggregator):
    if aggregator:
        return aggregator.validate()
    return


@chain
def validate_properties(aggregator):
    if aggregator:
        return aggregator.validate()
    return


@chain
def validate_parameters(aggregator):
    if aggregator:
        return aggregator.validate()
    return


@chain
def validate_manufacturings(aggregator):
    if aggregator:
        return aggregator.validate()
    return


@chain
def validate_measurements(aggregator):
    if aggregator:
        return aggregator.validate()
    return


@chain
def validate_metadata(aggregator):
    if aggregator:
        return aggregator.validate()
    return




@chain
def build_results(data):
    total_node_list = []
    uid = 0
    for key, node_list in data.items():
        if node_list is None:
            continue
        if node_list.nodes is None:
            continue
        for i in node_list.nodes:
            # Initialize node with basic structure
            node = {
                'label': i.__class__.__name__.strip('Node').lower(),
                'id': str(uid),
                'attributes': {k: v for k, v in dict(i.attributes).items() if v not in ([], None)}  # Filter out empty or None values upfront
            }

            # Refactor attributes processing for efficiency and clarity
            node['attributes'] = {
                attribute: [{'value': str(el.value), 'index': str(el.index)} for el in value] if isinstance(value, list)
                else [{'value': str(value.value), 'index': str(value.index)}]
                for attribute, value in node['attributes'].items() if value not in ([], None)
            }

            print(node)

            uid = uid + 1
            total_node_list.append(node)
    print(total_node_list)

    return {'nodes': total_node_list, 'relationships': []}


class NodeExtractor(TableDataTransformer):

    def __init__(self, ReportClass=NodeExtractionReport, **kwargs):
        self.node_list = []
        super().__init__(ReportClass=NodeExtractionReport, **kwargs)

    def process_aggregator(self, data_type, aggregator_class):
        if data_type in self.iterable and self.iterable[data_type]:
            data = self.iterable[data_type]
            context = self.context
            grouped_data = self.group_by_prefix(data) if data_type == "property" else {None: data}
            for entries in grouped_data.values():
                aggregator = aggregator_class(entries, context)
                return aggregator

    def get_table_understanding(self):

        chain = RunnableParallel(
            propertyNodes=aggregate_properties | validate_properties,
            matterNodes=aggregate_matters | validate_matters,
            parameterNodes=aggregate_parameters | validate_parameters,
            manufacturingNodes=aggregate_manufacturing | validate_manufacturings,
            measurementNodes=aggregate_measurement | validate_measurements,
            metadataNodes=aggregate_metadata | validate_metadata
        ) | build_results
        chain = chain.with_config({"run_name": "node-extraction"})
        self.node_list = chain.invoke({
            'input': self.iterable,
            'context': self.context,
        })

    @property
    def iterable(self):
        # Group elements by label.
        grouped_by_label = defaultdict(list)
        for index, element in enumerate(self.data):
            label = element['1_label']
            grouped_by_label[label].append(element)

        # Sort the dictionary by label.
        sorted_grouped_by_label = dict(sorted(grouped_by_label.items()))

        # Modify data for sorted groups.
        modified_data = {key: [
            {
                'header': element['header'],
                'column_values': element['column_values'][:3],
                'attribute': element.get('1_attribute'),
                'index': element.get('index')
            }
            for index, element in enumerate(value)
        ]
            for key, value in sorted_grouped_by_label.items()}
        return modified_data

    def _pre_check(self, element, **kwargs):
        if element['attribute'] is None:
            return True
        return False

    def build_results(self):
        self._results = self.node_list

    def run(self):
        self.get_table_understanding()
        self.build_results()
