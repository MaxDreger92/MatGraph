import json
import os
import re
from collections import defaultdict

from langchain.chains import create_structured_output_runnable
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import SystemMessagePromptTemplate, ChatPromptTemplate, PromptTemplate
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

    def create_query(self):
        return f"""
        Context: {self.context}
    
        Table:
        {", ".join(self.header)}
        {", ".join(self.row)}
        
        {self.additional_context}
        """

    def validate(self):
        pass

    def aggregate(self):
        print("Aggregating")
        query = self.create_query()
        llm = ChatOpenAI(model_name="gpt-4-1106-preview", openai_api_key=os.environ.get("OPENAI_API_KEY"))
        setup_message = self.setup_message
        prompt = ChatPromptTemplate.from_messages(setup_message)
        structured_llm = create_structured_output_runnable(self.schema, llm, prompt)
        output = structured_llm.invoke({"input": query})
        # print(query)
        # print(self.__class__, output)
        # print(self.__class__, len(output.instances))
        return output

    def create_node_list(self, string):
        # Preprocess the string
        processed_string = string
        pattern = r'```python\s+(.*?)\s+```'
        processed_string = re.search(pattern, processed_string, re.DOTALL).group(1)

        # Replace single backslashes with double backslashes
        processed_string = processed_string.replace('\\', '\\\\')

        # Try to load the JSON to check for errors
        try:
            self.node_list = json.loads(processed_string, strict=False)
            for i, node in enumerate(self.node_list):
                node['label'] = self.label
                if node['name'][0][1] == "inferred":
                    print("Node:", node, "i:", i, self.node_list)
                    node['id'] = f"inferred_{self.label}_{i}"
                else:
                    node['id'] = str(node['name'][0][1])
                keys_to_keep = ['label', 'id', 'attributes']

                updated_node = {'name': [{'value': name[0], 'index': name[1]} for name in node['name']],
                                'attributes': {key: value for key, value in node.items() if key not in ['label', 'id']},
                                **{key: value for key, value in node.items() if key in keys_to_keep}
                                }
                self.node_list[i] = updated_node
            for i, node in enumerate(self.node_list):
                updated_attributes = {}
                for key, value in node['attributes'].items():
                    if isinstance(value[0], list):
                        updated_attributes[key] = []
                        for attribute in value:
                            updated_attributes[key].append({'value': attribute[0], 'index': attribute[1]})
                    else:
                        print("value", value)
                        updated_attributes[key] = {'value': value[0], 'index': value[1]}
                self.node_list[i]['attributes'] = updated_attributes
            print("Changed Node List:", self.node_list)


        except json.JSONDecodeError as e:
            print("Error parsing JSON:", str(e))
            # Handle the error or return None to indicate failure

    @chain
    def validate(self):
        pass

    def run(self):
        query = self.create_query()
        print("Queryy", query)
        self.aggregate(query)
        self.validate()


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

    # def create_node_list(self, string):
    #     super.create_node_list(string)
    #     for node in self.node_list:
    #         if "measurement_condition" in node.keys():
    #             parameter_node = {
    #                 "label": "Parameter",
    #                 **node['measurement_condition']
    #             }
    #             self.node_list.append(parameter_node)


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
def validate_matters(data):
    return data


@chain
def validate_properties(data):
    print("Validating Properties", data)
    return data


@chain
def validate_parameters(data):
    return data


@chain
def validate_manufacturings(data):
    return data


@chain
def validate_measurements(data):
    return data


@chain
def validate_metadata(data):
    return data

def attribute_to_dict(obj):
    # If the object has attributes like 'name' and 'index', but not 'value'.
    if hasattr(obj, "__dict__") and 'index' in obj.__dict__ and not hasattr(obj, 'value'):
        name_like_attr = next((attr for attr in obj.__dict__ if attr != 'index'), None)
        if name_like_attr:
            return {'value': str(getattr(obj, name_like_attr)), 'index': str(obj.index)}

    # If the object is a list, recursively process each item in the list.
    elif isinstance(obj, list):
        # If the list is empty, return None to indicate no value.
        if len(obj) == 0:
            return None
        processed_list = [attribute_to_dict(item) for item in obj]
        # If the processed list contains only one item, return that item directly instead of a list.
        return processed_list if len(processed_list) > 1 else processed_list[0]

    # If the object has a __dict__ attribute, indicating it's a class instance.
    elif hasattr(obj, "__dict__"):
        result = {}
        for key, value in obj.__dict__.items():
            # Process only if the value is not None or the key specifically needs to be included.
            processed_value = attribute_to_dict(value)
            if processed_value is not None or key == 'names':
                result[key] = processed_value
        # Return the processed dictionary.
        return result

    # If the object does not match any of the above conditions, return it as is.
    else:
        if obj is None:
            return None
        return str(obj)

@chain
def build_results(data):
    print("Building Results", data)
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
    print("Node List", node_list)

    return {'nodes': node_list, 'relationships': []}

class NodeExtractor(TableDataTransformer):

    def __init__(self, ReportClass=NodeExtractionReport, **kwargs):
        self.node_list = []
        super().__init__(ReportClass=NodeExtractionReport, **kwargs)

    def process_aggregator(self, data_type, aggregator_class):
        print(self.iterable, "Data Type", data_type)
        if data_type in self.iterable and self.iterable[data_type]:
            data = self.iterable[data_type]
            context = self.context

            grouped_data = self.group_by_prefix(data) if data_type == "property" else {None: data}
            print("Grouped Data", grouped_data)
            for entries in grouped_data.values():
                aggregator = aggregator_class(entries, context)
                return aggregator

    def get_table_understanding(self):

        chain = RunnableParallel(
            properties=aggregate_properties | validate_properties,
            matters=aggregate_matters | validate_matters,
            parameters=aggregate_parameters | validate_matters,
            manufacturings=aggregate_manufacturing | validate_manufacturings,
            measurements=aggregate_measurement | validate_measurements,
            metadata=aggregate_metadata | validate_metadata
        ) | build_results

        self.node_list = chain.invoke({'input': self.iterable, 'context': self.context,
                      'additional_context': ["self.additional_context", "miau"]})

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
