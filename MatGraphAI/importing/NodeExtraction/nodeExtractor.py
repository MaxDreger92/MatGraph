import os
from collections import defaultdict

from langchain.chains import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain, RunnableParallel
from langchain_openai import ChatOpenAI

from graphutils.general import TableDataTransformer
from importing.NodeExtraction.schema import Metadata, \
    Properties, Measurements, Manufacturings, Parameters, Matters
from importing.NodeExtraction.setupMessages import MATTER_AGGREGATION_MESSAGE, PROPERTY_AGGREGATION_MESSAGE, \
    PARAMETER_AGGREGATION_MESSAGE, MANUFACTURING_AGGREGATION_MESSAGE, MEASUREMENT_AGGREGATION_MESSAGE
from importing.models import NodeExtractionReport


class NodeAggregator:
    def __init__(self, data, context, setup_message, additional_context):
        self.header = [f"{element['header']} ({element['attribute']}, {element['index']})" for element in data]
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
    
        Table:
        {", ".join(self.header)}
        {", ".join(self.row)}
        
        {self.additional_context}
        """

    @property
    def intermediate(self):
        return self._intermediate

    @intermediate.setter
    def intermediate(self, data):
        self._intermediate = data

    def validate(self):
        print("Validating")
        print(self.intermediate)
        return self.intermediate

    def aggregate(self):
        query = self.create_query()
        llm = ChatOpenAI(model_name="gpt-4-1106-preview", openai_api_key=os.environ.get("OPENAI_API_KEY"))
        setup_message = self.setup_message
        prompt = ChatPromptTemplate.from_messages(setup_message)
        chain = create_structured_output_runnable(self.schema, llm, prompt).with_config(
            {"run_name": f"{self.schema}-extraction"})
        self.intermediate = chain.invoke({"input": query})
        return self


class MatterAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=MATTER_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "matter"
        self.schema = Matters


class PropertyAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=PROPERTY_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "property"
        self.schema = Properties


class ParameterAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=PARAMETER_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "parameter"
        self.schema = Parameters


class ManufacturingAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=MANUFACTURING_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "manufacturing"
        self.schema = Manufacturings


class MeasurementAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=MEASUREMENT_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "measurement"
        self.schema = Measurements


class MetadataAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 setup_message=PARAMETER_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, setup_message, additional_context)
        self.label = "metadata"
        self.schema = Metadata


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


def attribute_to_dict(obj):
    # Handle class instances with specific attributes.
    if hasattr(obj, "__dict__"):
        # Special case for objects with 'index' but not 'value'.
        if 'index' in obj.__dict__ and not hasattr(obj, 'value'):
            name_attr = next((attr for attr in obj.__dict__ if attr != 'index'), None)
            if name_attr:
                return {'value': str(getattr(obj, name_attr)), 'index': str(obj.index)}
        # General case for objects with other attributes.
        result = {}
        for key, value in obj.__dict__.items():
            processed_value = attribute_to_dict(value)
            # Include keys with non-None values or explicitly required keys.
            if processed_value is not None or key == 'names':
                result[key] = processed_value
        return result if result else None  # Return None if result is empty.

    # Handle lists.
    elif isinstance(obj, list):
        if not obj:  # Short-circuit for empty lists.
            return None
        processed_list = [attribute_to_dict(item) for item in obj]
        return processed_list if len(processed_list) > 1 else processed_list[0]

    # Base case for handling simple data types and None.
    return None if obj is None else str(obj)


@chain
def build_results(data):
    node_list = []
    uid = 0
    for list in data.values():
        if not list:
            continue
        for i in list.instances:
            print(i)
            print(type(i))
            node = {
                'id': str(uid),
                'label': i.__class__.__name__.lower(),
                **attribute_to_dict(i)
            }
            uid = uid + 1
            node_list.append(node)

    return {'nodes': node_list, 'relationships': []}


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
            properties=aggregate_properties | validate_properties,
            matters=aggregate_matters | validate_matters,
            parameters=aggregate_parameters | validate_parameters,
            manufacturings=aggregate_manufacturing | validate_manufacturings,
            measurements=aggregate_measurement | validate_measurements,
            metadata=aggregate_metadata | validate_metadata
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
