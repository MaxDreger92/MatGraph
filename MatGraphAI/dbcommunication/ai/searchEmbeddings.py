import itertools
import logging
import os
from pprint import pprint

from dotenv import load_dotenv
from neomodel import db

from dbcommunication.ai.config import EMBEDDING_DIMENSIONS
from dbcommunication.ai.createEmbeddings import request_embedding
from matgraph.models.ontology import EMMOMatter
# loads embeddings for a model into RAM and enables fast search using FAISS
# index is fetched and built on instance creation


class WorkflowSearch:
    def __init__(self, models, fetch_filter="true"):
        """
        Initialize the WorkflowSearch instance.

        Args:
            models (dict): The Django model classes to fetch embeddings for, keyed by node type.
            fetch_filter (str): The filter to apply when fetching embeddings from the database.
        """
        print("Initializing WorkflowSearch")
        self.models = models
        self.fetch_filter = fetch_filter

        # Initialize an embedding search instance for each model
        self.embedding_searches = {node_type: EmbeddingSearch(Model, fetch_filter)
                                   for node_type, Model in models.items()}
        print("Initialized WorkflowSearch")
    def search_workflow(self, workflow_dict):
        """
        Search for a workflow matching the input queries.

        Args:
            workflow_dict (dict): A dictionary defining the workflow.

        Returns:
            A list of workflow ids that match the queries.
        """

        # Get the closest matches for each node in the workflow_dict
        node_matches = {}
        for node_type, nodes in workflow_dict['nodes'].items():
            search = self.embedding_searches[node_type]
            node_matches[node_type] = [search.find_string(node['name']) for node in nodes]

        # Create a mapping from node ID to the corresponding uid
        node_id_to_uid = {}
        for node_type, node_list in workflow_dict['nodes'].items():
            for i, node in enumerate(node_list):
                node_id_to_uid[node['id']] = node_matches[node_type][i]

        # Update the relationships in the workflow_dict with the uids
        updated_relationships = {}
        for relationship, connection_list in workflow_dict['relationships'].items():
            updated_connections = []
            for connection in connection_list:
                updated_connection = {'connect': (node_id_to_uid[connection['connect'][0]],
                                                  node_id_to_uid[connection['connect'][1]])}
                if 'value' in connection:
                    updated_connection['value'] = connection['value']
                updated_connections.append(updated_connection)
            updated_relationships[relationship] = updated_connections

        # Combine the matches to find workflows that contain all the matched nodes
        # The implementation of this step would depend on how your workflows are structured in the database
        workflows = self.find_workflows(node_matches, updated_relationships)

        return workflows


    def find_workflows(self, node_matches, relationships):
        """
        Given a dictionary of matched node ids for each node type, find workflows that contain all these nodes.

        Args:
            node_matches (dict): A dictionary containing the matched node ids for each node type.
            relationships (dict): A dictionary defining the relationships between nodes in the workflow.

        Returns:
            A list of workflow ids.
        """

        # Use the node_matches and relationships to build a Cypher query
        # First, find all nodes connected to the EMMOMatter, EMMOProcess, and EMMOQuantity nodes by a IS_A relationship
        connected_nodes = {}
        for node_type, node_ids in node_matches.items():
            for node_id in node_ids:
                query = f'''
                        MATCH (n:{node_type} {{uid: \'{node_id}\'}})<-[:IS_A]-(o)
                        RETURN o.uid, labels(o)[0]
                    '''
                result, _ = db.cypher_query(query)
                connected_nodes[node_id] = [[row[0] for row in result if row[0] is not None], result[0][1]]

        # Finally, for each connected_node, find all paths that follow the relationship_patterns
        match = []
        filter = []
        workflows = []
        output = []
        for rel_type, rels in relationships.items():
            for rel in rels:
                from_node_id, to_node_id = rel['connect']
                from_node_label = connected_nodes[from_node_id][1]
                to_node_label = connected_nodes[to_node_id][1]
                from_node_list = connected_nodes[from_node_id][0]
                to_node_list = connected_nodes[to_node_id][0]
                match.append(f'''(n{from_node_id.replace('-', '')}:{from_node_label})-[:{rel_type}]->(n{to_node_id.replace('-', '')}:{to_node_label})''')
                filter.append(f'''n{from_node_id.replace('-', '')}.uid IN {from_node_list} AND n{to_node_id.replace('-', '')}.uid IN {to_node_list} ''')

        output = [f'''n{node.replace('-', '')}.uid as n{node.replace('-', '')}''' for node in connected_nodes.keys()]

        query = f''' MATCH {",".join(match)} \n WHERE {' AND '.join(filter)} \n RETURN DISTINCT {', '.join(output)}'''
        result, _ = db.cypher_query(query)
        workflows.extend(result)

        return workflows







def main():
    from matgraph.models.ontology import EMMOProcess

    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    load_dotenv()
    from neomodel import config

    config.DATABASE_URL = os.getenv('NEOMODEL_NEO4J_BOLT_URL')
    # query = 'Fbrition'
    # search = EmbeddingSearch(EMMOProcess, fetch_filter="true", id_property='uid')
    # print(f'Searching for \'{query}\' now!')
    # result = search.find_string(query, include_similarity= True, return_model= True)
    # print(f'Found \'{result[0].__label__}\' node with the name \'{result[0].name}\' and the uid \'{result[0].uid}\'')

    workflow_dict = {
        'nodes':  {
            'EMMOMatter': {
                'educt':[
                    {'id': 1, 'name': "Platinum Catalyst"},
                    {'id': 3, 'name': "Ethanol"}
                ],
                'intermediates': [],
                'product': [
                    {'id': 5, 'name': "CatalystInk"}
                ]},
            'EMMOProcess': [
                {'id': 2, 'name': "Fabrication"}
            ]
        },
        'relationships': {'IS_MANUFACTURING_INPUT': [{'connect' : (1, 2)}, {'connect' : (3, 2)}],
                          'HAS_MANUFACTURING_OUTPUT': [{'connect' : (2, 5)}]},

    }

    workflow_search = WorkflowSearch({'EMMOMatter': EMMOMatter, 'EMMOProcess': EMMOProcess})
    result = workflow_search.search_workflow(workflow_dict)
    print(result)

    data_schema = {'nodes':
         {
             'EMMOMatter': [], # This is a material for example a catalyst
             'EMMOProcess': [], # parent class of Manufacturing and Measurement
             'EMMOManufacturing': [], # This is a manufacturing process that descrivbes the steps from the educts to the products for example coating of a catalyst layer
             'EMMOMeasuerment': [], # This is a measurement of the material for example electron microscopy of a material
             'EMMOParameter': [], # This is a parameter of the process for example temperature of the process
             'EMMOProperty': [], # This is a property of the material for example density of the material
         },
        'relationships':
            {
                'HAS_MANUFACTURING_OUTPUT': [], # This is a relationship between the manufacturing process and the material
                'IS_MANUFACTURING_INPUT': [], # This is a relationship between the manufacturing process and the material
                'HAS_MEASUREMENT_OUTPUT': [], # This is a relationship between the measurement and the material
                'IS_MEASUREMENT_INPUT': [], # This is a relationship between the measurement and the material
                'HAS_PARAMETER': [], # This is a relationship between the manufacturing process and the parameter
                'HAS_PROPERTY': [], # This is a relationship between the material and the property
            }
    }



if __name__ == '__main__':
    main()
