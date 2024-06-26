import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from matching.matcher import Matcher
from matgraph.models.ontology import EMMOMatter, EMMOProcess, EMMOQuantity


# Improved DataFrame creation and manipulation
def create_dataframe(combinations, attributes, columns):
    df_combinations = pd.DataFrame(combinations, columns=columns).drop_duplicates()
    df_attributes = pd.DataFrame(attributes, columns=['UID', 'Value', 'Attribute']).drop_duplicates(['UID', 'Attribute'])
    return df_combinations, df_attributes

def pivot_and_merge(df_combinations, df_attributes, columns):
    df_pivoted = df_attributes.pivot(index='UID', columns='Attribute', values='Value').reset_index()
    for column in columns:
        df_combinations = pd.merge(df_combinations, df_pivoted, how='left', left_on=column, right_on='UID').drop('UID', axis=1)
    return df_combinations.dropna(axis=1, how='all')

def generate_columns(max_len):
    half_len = max_len // 2
    uid_columns = [f'UID_{i+1}' for i in range(half_len)]
    name_columns = [f'name_{i+1}' for i in range(half_len)]
    return uid_columns + name_columns

def create_table_structure(data):
    combinations, attributes = data[0][0], data[0][1]
    max_len = max(map(len, combinations))
    columns = generate_columns(max_len)
    df_combinations, df_attributes = create_dataframe(combinations, attributes, columns)
    final_df = pivot_and_merge(df_combinations, df_attributes, columns)
    final_df = final_df[final_df.columns.drop(list(final_df.filter(regex='UID')))]
    final_df.to_csv('output_filename.csv', index=False)
    return final_df




ONTOMAPPER = {"matter": "EMMOMatter",
              "manufacturing": "EMMOProcess",
              "measurement": "EMMOProcess",
              "property": "EMMOQuantity",
                "parameter": "EMMOQuantity"
              }

RELAMAPPER = {"IS_MANUFACTURING_INPUT": "IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT",
              "IS_MANUFACTURING_OUTPUT": "IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT",
              "HAS_PARAMETER": "HAS_PARAMETER",
              "HAS_PROPERTY": "HAS_PROPERTY"}

OPERATOR_MAPPING = {
    '=': '=',
    '!=': '<>',
    '>': '>',
    '>=': '>=',
    '<': '<',
    '<=': '<='
}


FILTER_ONTOLOGY = """
$id.uid IN $uids
"""

FILTER_RELATION = """
($id)-[:$relation]->($id2)
"""

RETURN = """
$id as id
"""

class FabricationWorkflowMatcher(Matcher):
    def __init__(self, workflow_list, count=False, **kwargs):
        """
        Initialize the FabricationWorkflowMatcher.

        Args:
            workflow_list (dict): A dictionary containing nodes and relationships of the workflow.
            count (bool): A flag indicating whether to count the results.
            **kwargs: Additional arguments to be passed to the parent class.
        """
        self.query_list = [
            {
                **node,
                'uid': self.get_node_uid(node)
            }
            for node in workflow_list['nodes']
        ]
        self.relationships = workflow_list['relationships']
        self.count = count
        super().__init__(**kwargs)

    def get_node_uid(self, node):
        """
        Retrieve the UID for a given node based on its label.

        Args:
            node (dict): The node from which to retrieve the UID.

        Returns:
            str: The UID of the node or 'nope' if not found.
        """
        label = ONTOMAPPER.get(node['label'])
        name_value = node['attributes']['name']['value']

        node_classes = {
            'EMMOMatter': EMMOMatter,
            'EMMOProcess': EMMOProcess,
            'EMMOQuantity': EMMOQuantity
        }

        node_class = node_classes.get(label)
        if node_class:
            try:
                return node_class.nodes.get_by_string(string=name_value, limit=10)[0].uid
            except IndexError:
                return 'nope'
        return 'nope'

    def build_ontology_query(self, node):
        """
        Build an ontology query for a given node.

        Args:
            node (dict): The node for which to build the query.

        Returns:
            str: The Cypher query for the node.
        """
        node_id, label = node['id'], node['label']
        return f"(onto_{node_id}: {ONTOMAPPER[label]} {{uid: '{node['uid']}'}})"

    def build_tree_query(self, node_id, label):
        """
        Build a tree query to retrieve all hierarchical relationships for a node.

        Args:
            node_id (str): The ID of the node.
            label (str): The label of the node.

        Returns:
            str: The Cypher tree query for the node.
        """
        return f"""CALL {{
        WITH onto_{node_id}
        OPTIONAL MATCH (onto_{node_id})<-[:EMMO__IS_A*..]-(tree_onto_{node_id}:{ONTOMAPPER[label]})
        RETURN collect(DISTINCT tree_onto_{node_id}) + collect(DISTINCT onto_{node_id}) AS combined_{node_id}
        }}
        """

    def build_find_nodes_query(self, node_id, label, attributes):
        """
        Build a query to find nodes based on their attributes.

        Args:
            node_id (str): The ID of the node.
            label (str): The label of the node.
            attributes (dict): The attributes of the node.

        Returns:
            str: The Cypher query to find nodes based on attributes.
        """
        label = label.capitalize()
        if label in ['Property', 'Parameter']:
            value = attributes['value']['value']
            operator = OPERATOR_MAPPING[attributes['value']['operator']]
            return f"""CALL {{
            WITH combined_{node_id}
            UNWIND combined_{node_id} AS full_onto_{node_id}
            MATCH (full_onto_{node_id})<-[:IS_A]-(node_{node_id}:{label})
            WHERE toFloat(node_{node_id}.value) {operator} toFloat({value})
            RETURN collect(DISTINCT node_{node_id}) AS nodes_{node_id}
            }}
            """
        return f"""CALL {{
            WITH combined_{node_id}
            UNWIND combined_{node_id} AS full_onto_{node_id}
            MATCH (full_onto_{node_id})<-[:IS_A]-(node_{node_id}:{label})
            RETURN collect(DISTINCT node_{node_id}) AS nodes_{node_id}
            }}
            """

    def build_single_path_query(self, source, target, rel_type, index):
        """
        Build a query to find paths between source and target nodes.

        Args:
            source (str): The source node ID.
            target (str): The target node ID.
            rel_type (str): The relationship type.
            index (int): The index of the path.

        Returns:
            str: The Cypher query to find paths between source and target nodes.
        """
        path = f"path_{source}_{target}"
        uid_path = f"uids_path_{source}_{target}"
        return f"""
        CALL {{
        WITH nodes_{source}, nodes_{target}
        UNWIND nodes_{source} AS node_{source}
        UNWIND nodes_{target} AS node_{target}
        MATCH {path} = (node_{source})-[:{RELAMAPPER[rel_type]}*..8]->(node_{target})
        WITH collect(DISTINCT {path}) AS {path}
        RETURN {path}, [path IN {path} | [nodes(path)[0].uid, nodes(path)[-1].uid]] AS {uid_path}
        }}
        """

    def build_path_conditions(self, paths, uid_paths, relationships):
        """
        Build conditions for path queries to ensure correct matching.

        Args:
            paths (list): List of path queries.
            uid_paths (list): List of UID path queries.
            relationships (list): List of relationships.

        Returns:
            str: The Cypher query to build path conditions.
        """
        path_conditions = []
        return_statements = []
        idx_list = []

        for idx, rel in enumerate(relationships):
            idx_var = f"idx{idx}"
            idx_list.append(idx_var)
            source, target = rel['connection']
            uid_path = f"uids_path_{source}_{target}"
            path = f"path_{source}_{target}"
            return_statements.append(f"nodes({path}[idx[{idx}]])")

            for idx2, rel2 in enumerate(relationships):
                if idx == idx2:
                    continue
                source2, target2 = rel2['connection']
                uid_path2 = f"uids_path_{source2}_{target2}"

                if source == source2:
                    path_conditions.append(f"{uid_path}[{idx_var}][0] = {uid_path2}[idx{idx2}][0]")
                if target == target2:
                    path_conditions.append(f"{uid_path}[{idx_var}][-1] = {uid_path2}[idx{idx2}][-1]")
                if source == target2:
                    path_conditions.append(f"{uid_path}[{idx_var}][0] = {uid_path2}[idx{idx2}][-1]")

        path_condition = " AND ".join(path_conditions)
        unwind_statements = [f"UNWIND range(0, size({uid_path})-1) AS idx{i}" for i, uid_path in enumerate(uid_paths)]

        path_connector = f"""CALL {{
            WITH {', '.join(uid_paths)}
            {' '.join(unwind_statements)}
            WITH *
            WHERE {path_condition}
            RETURN collect(DISTINCT [{', '.join(idx_list)}]) AS idxs
        }}

        CALL {{
            WITH idxs, {', '.join(paths)}
            UNWIND idxs AS idx
            RETURN apoc.coll.toSet(apoc.coll.flatten([{', '.join(return_statements)}])) AS pathNodes
        }}
        """
        return path_connector

    def build_path_queries_and_conditions(self):
        """
        Build the queries and conditions for all paths in the workflow.

        Returns:
            str: The combined Cypher query for all paths and conditions.
        """
        paths, uid_paths = [], []
        path_queries = []

        for i, rel in enumerate(self.relationships):
            source, target = rel['connection']
            rel_type = rel['rel_type']
            paths.append(f"path_{source}_{target}")
            uid_paths.append(f"uids_path_{source}_{target}")

            path_queries.append(self.build_single_path_query(source, target, rel_type, i))

        path_connector = self.build_path_conditions(paths, uid_paths, self.relationships)
        return "\n".join(path_queries) + "\n" + path_connector

    def build_results_query(self):
        """
        Build the query to retrieve the results of the path matching.

        Returns:
            str: The Cypher query to retrieve the results.
        """
        return f"""
        WITH DISTINCT
        pathNodes,
        [NODE IN pathNodes | NODE.uid] + [x IN pathNodes | head([(x)-[:IS_A]->(neighbor) | neighbor.name])] AS combinations
        UNWIND pathNodes AS pathNode
        CALL apoc.case([
        pathNode:Matter,
        'OPTIONAL MATCH (onto)<-[:IS_A]-(pathNode)-[node_p:HAS_PROPERTY]->(property:Property)-[:IS_A]->(property_label:EMMOQuantity) RETURN DISTINCT [pathNode.uid, property.value, onto.name + "_" + property_label.name] as node_info',
        pathNode:Process,
        'OPTIONAL MATCH (onto)<-[:IS_A]-(pathNode)-[node_p:HAS_PARAMETER]->(property:Parameter)-[:IS_A]->(property_label:EMMOQuantity) RETURN DISTINCT [pathNode.uid, property.value, onto.name + "_" + property_label.name] as node_info'
        ])
        YIELD value AS node_info
        WITH DISTINCT collect(DISTINCT node_info['node_info']) AS node_info, combinations
        RETURN DISTINCT apoc.coll.toSet(collect(DISTINCT combinations)) AS combinations,
        apoc.coll.toSet(apoc.coll.flatten(collect(DISTINCT node_info))) AS metadata
        """

    def build_query(self):
        """
        Build the final query by combining ontology, tree, node, path, and results queries.

        Returns:
            tuple: The final Cypher query and an empty dictionary.
        """
        ontology_queries = [self.build_ontology_query(node) for node in self.query_list]
        tree_queries = [self.build_tree_query(node['id'], node['label']) for node in self.query_list]
        find_nodes_queries = [self.build_find_nodes_query(node['id'], node['label'], node['attributes']) for node in self.query_list]
        path_queries_and_conditions = self.build_path_queries_and_conditions()
        results_query = self.build_results_query()

        final_query = f"""MATCH {", ".join(ontology_queries)} 
        {" ".join(tree_queries + find_nodes_queries + [path_queries_and_conditions] + [results_query])}
        """
        print(final_query)
        return final_query, {}

    def build_result(self):
        """
        Build the result table from the database result.

        Returns:
            pandas.DataFrame: The result table.
        """
        return create_table_structure(self.db_result)

    def build_results_for_report(self):
        """
        Build the results for the report.

        Returns:
            tuple: List of results and columns.
        """
        result = create_table_structure(self.db_result)
        return result.values.tolist(), result.columns

    def build_extra_reports(self):
        """
        Placeholder for building extra reports if needed.
        """
        pass
