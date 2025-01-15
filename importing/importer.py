import csv
from datetime import timezone
import time
from io import StringIO
from pprint import pprint

import pandas as pd
from annoying.decorators import render_to
from django.template.loader import render_to_string
from neomodel import db

from importing.NodeAttributeExtraction.attributeClassifier import AttributeClassifier
from importing.NodeExtraction.nodeExtractor import NodeExtractor
from importing.NodeLabelClassification.labelClassifier import NodeClassifier
from importing.OntologyMapper.OntologyMapper import OntologyMapper, OntologyPipeline
from importing.RelationshipExtraction.completeRelExtractor import fullRelationshipsExtractor
from importing.models import ImportingReport, LabelClassificationReport
from importing.utils.openai import chat_with_gpt4, chat_with_gpt3
from matgraph.models.metadata import File
from matgraph.models.ontology import EMMOMatter, EMMOProcess, EMMOQuantity


class Importer:
    """
    A generic Importer class to run query and generate reports.
    Subclasses should implement build_query method to provide custom queries.
    """

    type = 'generic'  # type attribute for Importer. It's 'generic' for base Importer class.

    def __init__(self, data, paginator=None, force_report=False):
        """
        Initialize the Importer instance.

        Args:
            paginator: Paginator instance to apply pagination on query result.
            force_report (bool): Flag to determine whether to generate report or not.
        """

        self.paginator = paginator
        self.generate_report = force_report
        self.report = ''
        self.data = data
        self.db_results = None

    def build_query(self):
        """
        Method to build query.
        This method should be implemented in subclasses.
        """
        raise NotImplementedError()

    def _build_query_report(self, query, params, start, end):
        """
        Helper method to build report for the query executed.

        Args:
            query (str): The executed query.
            params (dict): The parameters used in the query.
            start (float): Start time of query execution.
            end (float): End time of query execution.
        """


        self.report += render_to_string('reports/query.html', {
            'query': query,
            'params': params,
            'date': timezone.now(),
            'duration': f'{round((end-start)*1000)}ms',
            # 'config': config,
            'paginator': self.paginator
        })

    def _build_result_report(self):
        """
        Helper method to build report for the result.
        """
        results, columns = self.build_results_for_report()

        self.report += render_to_string(
            'reports/results.html',{
                'label': 'Results',
                'columns': columns,
                'rows': results
            }
        )

    def build_results_for_report(self):
        """
        Method to build results for the report.

        Returns:
            A tuple of (db_results, db_columns).
        """
        return self.db_results, self.db_columns

    def build_extra_reports(self):
        """
        Method to build extra reports.
        This method can be implemented in subclasses to provide custom reports.
        """
        pass

    def run(self):
        """
        Method to execute the query and generate the report.
        """
        query, params = self.build_query()


        start = time.time()
        self.db_result, self.db_columns = db.cypher_query(query, params)
        print(self.db_result, self.db_columns)
        end = time.time()


        if self.generate_report:
            self._build_query_report(query, params, start, end)
            self._build_result_report()
            self.build_extra_reports()

            ImportingReport(
                type=self.type,
                report=self.report
            ).save()

    def build_result(self):
        """
        Method to build the result.

        Returns:
            db_results.
        """
        return self.db_results

    @property
    def result(self):
        """
        Property method to get the result.

        Returns:
            The result of build_result method.
        """
        return self.build_result()

class TableTransformer:
    """
    A Table Transformer class to transform the table data into structured JSON data following the schema:
    {
      "nodes": [
        {
          "id": "node1",
          "type": "TypeA",
          "name": "Name1"
        },
        {
          "id": "node2",
          "type": "TypeB",
          "name": "Name2"
        }
        // ... other nodes
      ],
      "relationships": [
        {
          "source": "node1",
          "target": "node2",
          "type": "REL_TYPE_1"
        }
        // ... other relationships
      ]
    }
    """
    def __init__(self, file, context, file_link, file_name):
        """
        Initialize the TableTransformer instance.

        Args:
            data (dict): The table data.
        """

        self.file = file
        self.context = context
        self.file_link = file_link
        self.file_name = file_name

    @property
    def predicted_labels(self):
        """
        Property method to get the predicted labels.

        Returns:
            The predicted labels.
        """
        if not hasattr(self, '_predicted_labels'):
            self.classify_node_labels()
        return self._predicted_labels
    def create_data(self):
        """
        Method to check the format of the table data.
        This method should be implemented in subclasses.
        """
        try:
            # Reset the file pointer to the start of the file
            self.file.seek(0)

            # Read the CSV data into a DataFrame
            self._data = pd.read_csv(self.file, header=None)
            return True


        except Exception as e:
            print(f"Error: {e}")
            return False

    @property
    def data(self):
        """
        Property method to get the data.

        Returns:
            The data.
        """
        return self._data

    @property
    def data_id(self):
        """
        Property method to get the data id.

        Returns:
            The data id.
        """
        if not hasattr(self, '_data_id'):
            self._data_id = self.save_data()
        return self._data_id

    def classify_node_labels(self):
        self.node_classifier = NodeClassifier(data = self.data,
                                              context = self.context,
                                              file_link = self.file_link,
                                              file_name = self.file_name)
        self.node_classifier.run()
        self._predicted_labels  = self.node_classifier.results

    def classify_attributes(self):
        # print(self.predicted_labels)
        self.attribute_classifier = AttributeClassifier(
                                                        self.predicted_labels,
                                                        data = self.data,
                                                        context =self.context['context'],
                                                        file_link = self.context['file_link'],
                                                        file_name = self.context['file_name']
                                                        )
        self.attribute_classifier.run()
        self._predicted_attributes = self.attribute_classifier.results


    def create_node_list(self):
        print("create node_list attributes")
        self.node_extractor = NodeExtractor(data = self._predicted_attributes,
                                            context = self.context['context'],
                                            file_link = self.context['file_link'],
                                            file_name = self.context['file_name'])
        self.node_extractor.run()
        self._node_list = {"nodes": self.node_extractor.node_list}

    def create_relationship_list(self):
        print("create relationship list")
        # self.relationship_extractor = fullRelationshipsExtractor(self._node_list)
        # self._relationship_list = {'relationships': self.relationship_extractor.run()}
        self._relationship_list = {'relationships': [{'rel_type': 'HAS_PARAMETER', 'connection': ['0', '18']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['1', '20']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['2', '21']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['3', '23']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['4', '26']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['5', '28']}, {'rel_type': 'HAS_PARAMETER', 'connection': ['6', '33']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['7', '0']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['8', '1']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['10', '2']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['11', '3']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['12', '4']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['13', '0']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['14', '1']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['15', '2']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['16', '3']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['17', '4']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['18', '5']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['19', '5']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['20', '6']}, {'rel_type': 'IS_MANUFACTURING_INPUT', 'connection': ['21', '6']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['0', '9']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['1', '18']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['2', '9']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['3', '18']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['4', '9']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['5', '20']}, {'rel_type': 'IS_MANUFACTURING_OUTPUT', 'connection': ['6', '20']}]}


    def build_json(self):
        """
        Method to build results for the report.

        Returns:
            A tuple of (db_results, db_columns).
        """
        return {**self._node_list, **self._relationship_list}




class TableImporter(Importer):
    """
    A generic Importer class to run query and generate reports.
    Subclasses should implement build_query method to provide custom queries.
    """

    type = 'generic'  # type attribute for Importer. It's 'generic' for base Importer class.

    def __init__(self, data, file_link, context, paginator=None, force_report=False):
        """
        Initialize the Importer instance.

        Args:
            paginator: Paginator instance to apply pagination on query result.
            force_report (bool): Flag to determine whether to generate report or not.
        """
        self.ontology_mapper = OntologyPipeline(data, file_link, context)
        self.paginator = paginator
        self.generate_report = force_report
        self.report = ''
        self.data = self.prepare_data(file_link, data)
        self.file_link = file_link
        self.db_results = None
        self.ontology_mapper = {
            'matter': 'EMMOMatter',
            'manufacturing': 'EMMOProcess',
            'measurement': 'EMMOProcess',
            'parameter': 'EMMOQuantity',
            'property': 'EMMOQuantity'
        }

    def prepare_data(self, file_link, data):
        file = File.nodes.get(link=file_link)
        file_obj_bytes = file.get_file()

        # Decode the bytes object to a string
        file_obj_str = file_obj_bytes.decode('utf-8')

        # Use StringIO on the decoded string
        file_obj = StringIO(file_obj_str)
        csv_reader = csv.reader(file_obj)
        first_row = next(csv_reader)

        # Initialize a list of sets for each column
        column_values = [set() for _ in range(len(first_row))]

        for row in csv_reader:
            for i, value in enumerate(row):
                column_values[i].add(value)

        data['column_values'] = [list(column_set) for column_set in column_values]
        self.ontology_mapper.run()
        self.mapping = self.ontology_mapper.mapping

        return data

    def build_query(self):
        # Construct the base part of the query for loading the CSV
        base_query = f"LOAD CSV FROM '{self.file_link}' as row WITH row, toString(timestamp()) AS uniqueId WITH row, uniqueId SKIP 1"
        query_parts = [base_query]

        # Function to construct attribute value strings
        def format_attr_value(attr_value):
            print(attr_value)
            
            index_value = attr_value.get('index', 'inferred')
            
            if index_value == 'inferred' or index_value == "missing":
                return f"'{attr_value['value']}'"
            return f"row[{int(index_value)}]"


        # Construct the query for adding ontology relations
        ontology_mapping = str(self.mapping).replace("':", ":").replace("{'", "{").replace(", '", ", ").replace("-", "_")
        add_ontology = f"""WITH * UNWIND {ontology_mapping} as input
        MATCH (ontology:EMMOMatter|EMMOQuantity|EMMOProcess),
        (n:Matter|Parameter|Manufacturing|Measurement|Property)
        WHERE ontology.uid = input.id AND (n.name = input.name OR input.name in n.name)
        MERGE (n)-[:IS_A]->(ontology)
        """

        # Function to add attributes to nodes
        def construct_setter(attr_name, attr_values, node_id):
            single_value = len(attr_values) == 1
            setter_prefix = f"SET n{node_id}.{attr_name} = "
            if single_value:
                value = attr_values[0]
                print(attr_name, value, node_id)
                setter_value = format_attr_value(value)
                return setter_prefix + setter_value

            # For multiple values, construct an array and remove nulls
            value_strings = [format_attr_value(value) for value in attr_values]
            values_list = ", ".join(value_strings)
            return f"{setter_prefix}apoc.coll.removeAll([{values_list}], [null])"


        # Build queries for nodes and their attributes
        for node_config in self.data['nodes']:
            node_id, label = node_config['id'], node_config['label']
            query_parts.append(f"CREATE (n{node_id}:{label.capitalize()} {{uid: randomUUID(), flag: 'dev'}})")

            for attr_name, attr_values in node_config['attributes'].items():
                attr_values = [attr_values] if not isinstance(attr_values, list) else attr_values
                attr_values = [attr_value for attr_value in attr_values if attr_value['value'] != 'MISSING_VALUE_OR_OPERATOR']
                attribute_query = construct_setter(attr_name, attr_values, node_id)
                query_parts.append(attribute_query)

        # Build queries for relationships
        relationship_queries = [
            f"MERGE (n{rel['connection'][0]})-[:{rel['rel_type']}]->(n{rel['connection'][1]})"
            for rel in self.data['relationships']
        ]

        # Combine all parts of the query
        full_query = '\n'.join(query_parts + relationship_queries + [add_ontology])
        print(full_query)

        return full_query, {}

    def ingest_data(self):
        """
        Method to ingest data into the database.
        """
        query, params = self.build_query()
        start = time.time()
        self.db_results = db.run(query, **params)
        end = time.time()
        # self._build_query_report(query, params, start, end)

    def _build_query_report(self, query, params, start, end):
        """
        Helper method to build report for the query executed.

        Args:
            query (str): The executed query.
            params (dict): The parameters used in the query.
            start (float): Start time of query execution.
            end (float): End time of query execution.
        """
        # config = [
        #     (k, v('value') if callable(v) else v)
        #     for k, v in vars(sys.modules['matching.config']).items()
        #     if not k.startswith('_') and not k.startswith('QUERY')
        # ]

        self.report += render_to_string('reports/query.html', {
            'query': query,
            'params': params,
            'date': timezone.now(),
            'duration': f'{round((end-start)*1000)}ms',
            # 'config': config,
            'paginator': self.paginator
        })

    def _build_result_report(self):
        """
        Helper method to build report for the result.
        """
        results, columns = self.build_results_for_report()

        self.report += render_to