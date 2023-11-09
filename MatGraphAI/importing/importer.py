from datetime import timezone
import time

from annoying.decorators import render_to
from django.template.loader import render_to_string
from neomodel import db

from importing.NodeLabelClassification.labelClassifier import NodeClassifier
from importing.models import ImportingReport


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

        query = query.replace(
            '$pagination',
            self.paginator.build_query_fragment() if self.paginator else ''
        )

        start = time.time()
        self.db_result, self.db_columns = db.cypher_query(query, params)
        print(f'{query} \n \n {params}')
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
    def __init__(self, data):
        """
        Initialize the TableTransformer instance.

        Args:
            data (dict): The table data.
        """
        self.data = data

    def classify_nodes(self):
        self.node_classifier = NodeClassifier(self.data, )
class TableImporter(Importer):
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
        # Iterate through the list of nodes in the configuration
        query_parts = ["LOAD CSV FROM 'https://docs.google.com/spreadsheets/d/e/2PACX-1vT2wLudGdp-uSJ__NXR0lovJWP5gxA6EhyoVHtXQ7_DTLklpwIlA9ySMvF4ShZ6QE2ZSA1Dk7CPx6mu/pub?output=csv' AS row"]
    
        for node_config in self.data['nodes']:
            label = node_config['label']
            id = node_config['node_id']
            attributes = node_config['attributes']
            headers = self.data["headers"]
            # Construct the Cypher query for this node
            query_parts.append(
                f"CREATE (n{id}:{label} {{uid: randomUUID()}})")
            print(len(self.data["nodes"]))
    
            for attr_name, attr_values in attributes.items():
                for attr_config in attr_values:
                    if attr_config['position'][1] == 'header':
                        # If the attribute value is in the header, use the attribute name directly
                        query_parts.append(f"""SET n{id}.{attr_name} = '{headers[attr_config['position'][0]]}'""")
                    elif attr_config['position'][1] == 'column':
                        # If the attribute value is in a column, use the column index to access the value
                        query_parts.append(f"""SET n{id}.{attr_name} = row[{attr_config['position'][0]}]""")
        for rel in self.data['relationships']:
            rel_type = rel['rel_type']
            start_node = rel['connection'][0]
            end_node = rel['connection'][1]
            query_parts.append(f"""MERGE (n{start_node})-[r{start_node}{end_node}:{rel_type}]->(n{end_node})""")
    
        query = '\n'.join(query_parts)
        return query, {}

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