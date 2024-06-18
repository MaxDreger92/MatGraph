import os
from collections import defaultdict

from langchain.chains import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.runnables import chain, RunnableParallel
from langchain_openai import ChatOpenAI

from graphutils.config import CHAT_GPT_MODEL
from graphutils.general import TableDataTransformer
# from importing.NodeExtraction.dummydata import test_data
from importing.NodeExtraction.examples import MATTER_AGGREGATION_EXAMPLES, PARAMETER_AGGREGATION_EXAMPLES, \
    MANUFACTURING_AGGREGATION_EXAMPLES
from importing.NodeExtraction.nodeCorrector import MatterCorrector, PropertyCorrector, ParameterCorrector, \
    ManufacturingCorrector, MeasurementCorrector, MetadataCorrector, SimulationCorrector
from importing.NodeExtraction.schema import MatterNodeList, PropertyNodeList, ManufacturingNodeList, \
    MeasurementNodeList, MetadataNodeList, ParameterNodeList, MatterNode, MatterAttributes, Identifier, Name, \
    BatchNumber, Ratio, SimulationNodeList
from importing.NodeExtraction.setupMessages import MATTER_AGGREGATION_MESSAGE, PROPERTY_AGGREGATION_MESSAGE, \
    PARAMETER_AGGREGATION_MESSAGE, MANUFACTURING_AGGREGATION_MESSAGE, MEASUREMENT_AGGREGATION_MESSAGE, \
    METADATA_AGGREGATION_MESSAGE, SIMULATION_AGGREGATION_MESSAGE
from importing.models import NodeExtractionReport


class NodeAggregator:
    def __init__(self, data, context, header, first_row, setup_message, additional_context):
        self.data = data
        self.header = [f"{element['header']}" for element in data]
        self.attributes = [f"{element['attribute']}" for element in data]
        self.indices = [f"{element['index']}" for element in data]
        self.row = [element['column_values'][0] if element['column_values'] else '' for element in data]
        self.setup_message = setup_message
        self.context = context
        self.additional_context = additional_context
        self.conversation = self.setup_message
        self.headers = header
        self.first_row = first_row
        self.label = None
        self.schema = None
        self._intermediate = None

    def create_query(self):
        return f"""
        Context: 
            Domain: {self.context}
            Full Table: 
                column_index: {', '.join(self.indices)}
                headers: {', '.join(self.header)}
                first row: {', '.join(self.row)}
                
        
        Input Data: {[{"ColumnIndex": self.indices[i], 
                 "AttributeType": self.attributes[i], 
                 "TableHeader": self.header[i], 
                 "AttributeValue": self.row[i]} for i in range(len(self.header))]}
        
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

    from tenacity import retry, stop_after_attempt, wait_fixed
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def aggregate(self):
        """Performs the initial extraction of relationships using GPT-4."""
        print(f"Aggregate {self.schema} nodes")
        query = self.create_query()
        llm = ChatOpenAI(model_name=CHAT_GPT_MODEL, openai_api_key=os.getenv("OPENAI_API_KEY"))
        setup_message = self.setup_message
        prompt = ChatPromptTemplate.from_messages(setup_message)

        if self.examples:
            example_prompt = ChatPromptTemplate.from_messages([('human', "{input}"), ('ai', "{output}")])
            few_shot_prompt = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=self.examples)
            prompt = ChatPromptTemplate.from_messages([setup_message[0], few_shot_prompt, *setup_message[1:]])

        chain = create_structured_output_runnable(self.schema, llm, prompt).with_config(
            {"run_name": f"{self.schema}-extraction"})
        self.intermediate = chain.invoke({"input": query})
        print("Output", self.intermediate)
        print(f"Aggregated {self.schema} nodes")
        return {"input": {"header": self.header, "row": self.row, "attributes": self.attributes, "indices": self.indices}, "output": self.intermediate, "query": query}
        # return {'input': {'header': ['FuelCell_Id', 'MEA', 'Catalys Ink', 'Catalyst', 'Ionomer', 'I/C', 'Transfer substrate', 'Membrane', 'Anode', 'GDL'], 'row': ['RN0721-28', 'MEA', 'CatInk', 'F50E-HT', 'AQ', '0.7', 'Gore HCCM', 'MX10.15', 'Gore anode', 'HW4 B2.2'], 'attributes': ['identifier', 'identifier', 'name', 'name', 'name', 'name', 'name', 'identifier', 'name', 'batch_number'], 'indices': ['0', '4', '5', '8', '9', '11', '13', '14', '15', '16']},
        # 'output': MatterNodeList(nodes=[MatterNode(attributes=MatterAttributes(identifier=Identifier(AttributeValue='RN0721-28', AttributeReference=0), batch_number=None, ratio=None, concentration=None, name=[Name(AttributeValue='Fuel Cell', AttributeReference='header')])), MatterNode(attributes=MatterAttributes(identifier=Identifier(AttributeValue='MEA', AttributeReference=4), batch_number=None, ratio=None, concentration=None, name=[Name(AttributeValue='MEA Assembly', AttributeReference='header')])), MatterNode(attributes=MatterAttributes(identifier=None, batch_number=None, ratio=None, concentration=None, name=[Name(AttributeValue='CatInk', AttributeReference=5)])), MatterNode(attributes=MatterAttributes(identifier=None, batch_number=None, ratio=None, concentration=None, name=[Name(AttributeValue='F50E-HT', AttributeReference=8)])), MatterNode(attributes=MatterAttributes(identifier=None, batch_number=None, ratio=None, concentration=None, name=[Name(AttributeValue='AQ', AttributeReference=9)])), MatterNode(attributes=MatterAttributes(batch_number=None, concentration=None, name=[Name(AttributeValue=0.7, AttributeReference=11)], identifier=Identifier(AttributeValue='RN0721-28', AttributeReference=0))), MatterNode(attributes=MatterAttributes(identifier=None, batch_number=None, ratio=None, concentration=None, name=[Name(AttributeValue='Gore HCCM', AttributeReference=13)])), MatterNode(attributes=MatterAttributes(identifier=Identifier(AttributeValue='MX10.15', AttributeReference=14), batch_number=None, ratio=None, concentration=None, name=[Name(AttributeValue='Membrane', AttributeReference='header')])), MatterNode(attributes=MatterAttributes(identifier=None, batch_number=None, ratio=None, concentration=None, name=[Name(AttributeValue='Gore anode', AttributeReference=15)])), MatterNode(attributes=MatterAttributes(identifier=None, batch_number=BatchNumber(AttributeValue='HW4 B2.2', AttributeReference=16), ratio=None, concentration=None, name=[Name(AttributeValue='GDL', AttributeReference='header')]))]),
        # 'query': "\n        Context: \n            Domain: Fuel Cell Fabrication\n            Full Table: \n                headers: ['RN0721-28', 'CatalystInk Fabrication', 'MEA Assembly', 'Fuel Cell Assembly', 'MEA', 'CatInk', '6', '55', 'F50E-HT', 'AQ', '790', '0.7', '0.25', 'Gore HCCM', 'MX10.15', 'Gore anode', 'HW4 B2.2', 'Ford', '0.459', '0.477', '0.482', '0.493', '0.499', '0.519', '0.535', '0.59', '0.704', '0.754', '0.789', '0.93']\n                first row: ['FuelCell_Id', 'CatalystInk Fabrication', 'MEA Assembly', 'Fuel Cell Assembly', 'MEA', 'Catalys Ink', 'Drymill time (hrs)', 'Drying temp (deg C)', 'Catalyst', 'Ionomer', 'EW', 'I/C', 'Pt loading (mg/cm2geo)', 'Transfer substrate', 'Membrane', 'Anode', 'GDL', 'Station', 'HOT polarization_HOT 2.4 (V)', 'HOT polarization_HOT 2.1 (V)', 'HOT polarization_HOT 1.9 (V)', 'HOT polarization_HOT 1.7 (V)', 'HOT polarization_HOT 1.5 (V)', 'HOT polarization_HOT 1.2 (V)', 'HOT polarization_HOT 1.0 (V)', 'HOT polarization_HOT 0.6 (V)', 'HOT polarization_HOT 0.2 (V)', 'HOT polarization_HOT 0.1 (V)', 'HOT polarization_HOT 0.05 (V)', 'HOT polarization_HOT OCV (V)']\n                \n        \n        Input Data: [{'ColumnIndex': '0', 'AttributeType': 'identifier', 'TableHeader': 'FuelCell_Id', 'AttributeValue': 'RN0721-28'}, {'ColumnIndex': '4', 'AttributeType': 'identifier', 'TableHeader': 'MEA', 'AttributeValue': 'MEA'}, {'ColumnIndex': '5', 'AttributeType': 'name', 'TableHeader': 'Catalys Ink', 'AttributeValue': 'CatInk'}, {'ColumnIndex': '8', 'AttributeType': 'name', 'TableHeader': 'Catalyst', 'AttributeValue': 'F50E-HT'}, {'ColumnIndex': '9', 'AttributeType': 'name', 'TableHeader': 'Ionomer', 'AttributeValue': 'AQ'}, {'ColumnIndex': '11', 'AttributeType': 'name', 'TableHeader': 'I/C', 'AttributeValue': '0.7'}, {'ColumnIndex': '13', 'AttributeType': 'name', 'TableHeader': 'Transfer substrate', 'AttributeValue': 'Gore HCCM'}, {'ColumnIndex': '14', 'AttributeType': 'identifier', 'TableHeader': 'Membrane', 'AttributeValue': 'MX10.15'}, {'ColumnIndex': '15', 'AttributeType': 'name', 'TableHeader': 'Anode', 'AttributeValue': 'Gore anode'}, {'ColumnIndex': '16', 'AttributeType': 'batch_number', 'TableHeader': 'GDL', 'AttributeValue': 'HW4 B2.2'}]\n        \n        \n        "}


class MatterAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 first_row,
                 header,
                 setup_message=MATTER_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, header, first_row, setup_message, additional_context)
        self.label = "matter"
        self.schema = MatterNodeList
        self.examples = MATTER_AGGREGATION_EXAMPLES


class PropertyAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 first_row,
                 header,
                 setup_message=PROPERTY_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, first_row, header, setup_message, additional_context)
        self.label = "property"
        self.schema = PropertyNodeList
        self.examples = None


class ParameterAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 first_row,
                 header,
                 setup_message=PARAMETER_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, first_row, header, setup_message, additional_context)
        self.label = "parameter"
        self.schema = ParameterNodeList
        self.examples = PARAMETER_AGGREGATION_EXAMPLES


class ManufacturingAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 first_row,
                 header,
                 setup_message=MANUFACTURING_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, first_row, header, setup_message, additional_context)
        self.label = "manufacturing"
        self.schema = ManufacturingNodeList
        self.examples = MANUFACTURING_AGGREGATION_EXAMPLES


class MeasurementAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 first_row,
                 header,
                 setup_message=MEASUREMENT_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, first_row, header, setup_message, additional_context)
        self.label = "measurement"
        self.schema = MeasurementNodeList
        self.examples = None

class SimulationAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 first_row,
                 header,
                 setup_message=SIMULATION_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, first_row, header, setup_message, additional_context)
        self.label = "simulation"
        self.schema = SimulationNodeList
        self.examples = None


class MetadataAggregator(NodeAggregator):
    def __init__(self,
                 data,
                 context,
                 first_row,
                 header,
                 setup_message=METADATA_AGGREGATION_MESSAGE,
                 additional_context=""):
        super().__init__(data, context, first_row, header, setup_message, additional_context)
        self.label = "metadata"
        self.schema = MetadataNodeList
        self.examples = None


def group_by_prefix(self, data):
    grouped = defaultdict(list)
    for entry in data:
        prefix = entry['header'].split('_', 1)[0]
        grouped[prefix].append(entry)
    return grouped


def get_aggregator(iterable, data_type, aggregator_class, context, header, first_row):
    if data_type in iterable and iterable[data_type]:
        data = iterable[data_type]
        context = context

        grouped_data = group_by_prefix(data) if data_type == "property" else {None: data}
        for entries in grouped_data.values():
            aggregator = aggregator_class(entries, context, header, first_row)
            return aggregator


def aggregate_nodes(data, type, aggregator_class):
    if aggregator := get_aggregator(data['input'], type, aggregator_class, data['context'], data['first_line'], data['header']):
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
def aggregate_simulations(data):
    return aggregate_nodes(data, "Simulation", SimulationAggregator)


def validate_nodes(data, corrector_type):
    if data:
        corrector = corrector_type(input=data['input'], nodes=data['output'], query=data['query'])
        corrector.run()
        return corrector.corrected_nodes
    return


@chain
def validate_matters(data):
    return validate_nodes(data, MatterCorrector)


@chain
def validate_properties(data):
    return validate_nodes(data, PropertyCorrector)


@chain
def validate_parameters(data):
    return validate_nodes(data, ParameterCorrector)


@chain
def validate_manufacturings(data):
    return validate_nodes(data, ManufacturingCorrector)


@chain
def validate_measurements(data):
    return validate_nodes(data, MeasurementCorrector)


@chain
def validate_metadata(data):
    return validate_nodes(data, MetadataCorrector)

@chain
def validate_simulations(data):
    return validate_nodes(data, SimulationCorrector)



def process_attribute(value):
    """Process attribute based on its type."""
    if isinstance(value, list):
        return [
            {
                'value': str(el.AttributeValue).encode('unicode_escape').decode('ascii'),
                'index': str(el.AttributeReference).replace("guess", "inferred").replace("header", "inferred").replace("context", "inferred")
            }
            for el in value if hasattr(el, 'AttributeValue') and hasattr(el, 'AttributeReference')
        ]
    elif hasattr(value, 'AttributeValue') and hasattr(value, 'AttributeReference'):
        return [
            {
                'value': str(value.AttributeValue).encode('unicode_escape').decode('ascii'),
                'index': str(value.AttributeReference).replace("guess", "inferred").replace("header", "inferred").replace("context", "inferred")
            }
        ]
    else:
        # Fallback for unexpected attribute types
        return [{'value': str(value), 'index': 'inferred'}]

@chain
def build_results(data):
    total_node_list = []
    uid = 0
    for key, node_list in data.items():
        if not node_list or not getattr(node_list, 'nodes', None):
            continue

        for node_item in node_list.nodes:
            label = node_item.__class__.__name__.strip('Node').lower()
            node = {
                'label': label,
                'id': str(uid),
                'attributes': {}
            }

            # Populate node attributes
            raw_attributes = {k: v for k, v in vars(node_item).get('attributes', {}) if v not in ([], None)}
            for attribute, value in raw_attributes.items():
                processed_value = process_attribute(value)
                if processed_value:
                    node['attributes'][attribute] = processed_value

            total_node_list.append(node)
            uid += 1

    return total_node_list


# Example usage:
# build_results(data_from_your_application)


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
            'header': self.headers,
            'first_line': self.first_row
        })
        # self.node_list = test_data


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
        self._results = {"nodes": self.node_list, "relationships": []}

    def run(self):
        self.get_table_understanding()
        self.build_results()
