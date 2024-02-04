from collections import defaultdict
from pprint import pprint
from uuid import UUID
import os

import pandas as pd
from dotenv import load_dotenv


def create_table_structure(data):
    # Extract combinations and attributes
    combinations = data[0][0]
    attributes = data[0][1]
    print(f"Number of combinations: {len(combinations)}")

    # Dynamically generate column names based on the longest combination
    max_len = max(map(len, combinations))
    half_len = max_len // 2  # We assume max_len is always even for this to work

    uid_columns = [f'UID_{i+1}' for i in range(half_len)]
    name_columns = [f'name_{i+1}' for i in range(half_len)]

    columns = uid_columns + name_columns
    print(columns)
    print(combinations[0])
    # Convert combinations into a DataFrame

    df_combinations = pd.DataFrame(combinations, columns=columns)
    print(df_combinations)
    df_combinations = df_combinations.drop_duplicates(subset=columns)
    print(df_combinations)
    # return(df_combinations)
    # Convert attributes into a DataFrame
    df_attributes_raw = pd.DataFrame(attributes, columns=['UID', 'Value', 'Attribute'])
    df_attributes = df_attributes_raw.drop_duplicates(subset=['UID', 'Attribute'])


    # Pivot the attributes dataframe
    df_pivoted = df_attributes.pivot(index='UID', columns='Attribute', values='Value').reset_index()

    # Iteratively merge with the combinations dataframe on each UID
    for i, column in enumerate(columns):
        merged = pd.merge(df_combinations, df_pivoted, how='left', left_on=column, right_on='UID', suffixes=('', f'_y{i+1}'))
        # Drop the unnecessary UID column (which came from df_pivoted)
        merged.drop('UID', axis=1, inplace=True)
        df_combinations = merged

    # Drop columns that have only NaNs
    final_df = df_combinations.dropna(axis=1, how='all')

    # Drop all columns that contain the string 'UID'
    final_df = final_df[final_df.columns.drop(list(final_df.filter(regex='UID')))]


    final_df.to_csv('output_filename.csv', index=False)

    return final_df


# TODO implement filtering for values!
QUERY_BY_VALUE = """"""
from matching.matcher import Matcher
from matgraph.models.ontology import *

ONTOMAPPER = {"EMMOMatter": "Matter",
              "EMMOProcess": "Process",
                "EMMOQuantity": "Quantity"}

RELAMAPPER = {"IS_MANUFACTURING_INPUT": "IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT",
              "IS_MANUFACTURING_OUTPUT": "IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT",
              "HAS_PARAMETER": "HAS_PARAMETER",
              "HAS_PROPERTY": "HAS_PROPERTY"}


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
        print(workflow_list)
        self.query_list = [
            {
                **node,
                'uid': EMMOMatter.nodes.get_by_string(string = node['attributes']['name'], limit = 1)[0].uid if node['type'] == 'EMMOMatter' else
                EMMOProcess.nodes.get_by_string(string = node['attributes']['name'], limit = 1)[0].uid if node['type'] == 'EMMOProcess' else
                EMMOQuantity.nodes.get_by_string(string = node['attributes']['name'], limit = 1)[0].uid if node['type'] == 'EMMOQuantity' else 'nope'
            }
            for node in workflow_list
        ]
        self.count = count
        super().__init__(**kwargs)


    def build_query(self):
        match_query = []
        filter_node_query = []
        relationship_query = []
        with_query = []
        with_path_query = []
        conditions = []
        where_query = []
        match_onto_query = []
        with_onto_query = []
        match_only_onto_query = []
        for node in self.query_list:
            match_only_onto_query.append(f"""(onto_{node['id']}:{node['type']}{{uid: '{node['uid']}'}})""")
            where_query.append(f""" full_onto_{node['id']}.uid IN tree_uid_{node['id']}""")
            match_onto_query.append(f"""(tree_onto_{node['id']})-[:EMMO__IS_A*..]->(onto_{node['id']})""")
            with_onto_query.append(f"""apoc.coll.union(collect(tree_onto_{node['id']}), collect(onto_{node['id']})) as tree_{node['id']}, apoc.coll.union(collect( tree_onto_{node['id']}.uid), collect(onto_{node['id']}.uid)) as tree_uid_{node['id']}""")
            with_query.append(f""" node_{node['id']}""")
            if node['type'] == 'EMMOQuantity':
                match_query.append(f"""(full_onto_{node['id']})<-[:IS_A]-(node_{node['id']}:{ONTOMAPPER[node['type']]})<-[rel_{node['id']}:HAS_PARAMETER]-()""")
                where_query.append(f""" rel_{node['id']}.float_value {node['operator']} {node['value']}""")
            else:
                match_query.append(f"""(full_onto_{node['id']})<-[:IS_A]-(node_{node['id']}:{ONTOMAPPER[node['type']]})""")


        # Constructing the relationship paths                m
            for rel in node["relationships"]:
                if rel['connection'][0] == node['id']:
                    relationship_query.append(f"""path_{rel['connection'][0]}_{rel['connection'][1]} = ((node_{rel['connection'][0]})-[:{RELAMAPPER[rel['rel_type']]}*..5]->(node_{rel['connection'][1]}))""")
                    with_path_query.append(f""" path_{rel['connection'][0]}_{rel['connection'][1]}""")
        # 1. Create two dictionaries: one for path starts and one for path ends.
        path_groups_start = defaultdict(list)
        path_groups_end = defaultdict(list)

        # Group paths by their start and end node ids
        for path in with_path_query:
            start, end = path.split("_")[1], path.split("_")[2]
            path_groups_start[start].append(path)
            path_groups_end[end].append(path)

        conditions = []

        # 1. Check overlap between the end nodes of paths
        for end, end_paths in path_groups_end.items():
            if len(end_paths) > 1:  # More than one path sharing the same end node
                for i in range(len(end_paths)):
                    for j in range(i+1, len(end_paths)):
                        conditions.append(f"nodes({end_paths[i]})[-1].uid = nodes({end_paths[j]})[-1].uid")

                # 1. Check overlap between the end nodes of paths
        for start, start_paths in path_groups_start.items():
            if len(start_paths) > 1:  # More than one path sharing the same start node
                for i in range(len(start_paths)):
                    for j in range(i+1, len(start_paths)):
                        conditions.append(f"nodes({start_paths[i]})[0].uid = nodes({start_paths[j]})[0].uid")

        # 2. Check overlap between the start nodes of one path and the end nodes of another path
        for start, start_paths in path_groups_start.items():
            for end, end_paths in path_groups_end.items():
                if start == end:  # Ensure that we're not comparing a path to itself
                    for start_path in start_paths:
                        for end_path in end_paths:
                            conditions.append(f"nodes({start_path})[0].uid = nodes({end_path})[-1].uid")





    # Concatenating relationship paths to the nodes, and removing the last "->"

        # Construct the main query parts
        query = f"""
    MATCH {', '.join(match_only_onto_query)}
    WITH *
    OPTIONAL MATCH {' OPTIONAL MATCH '.join(match_onto_query)}
    WITH DISTINCT {', '.join(with_onto_query)}
    MATCH {', '.join(match_query)}
    WHERE {' AND '.join(where_query)}
    WITH DISTINCT {', '.join(with_query)}
    MATCH {' MATCH '.join(relationship_query)}
    {'WHERE ' + ' AND '.join(conditions) if len(conditions) != 0 else ''}
    WITH DISTINCT {', '.join(with_query)}, apoc.coll.toSet(apoc.coll.flatten([{', '.join(["nodes("+ path + ")" for path in  with_path_query])}])) as pathNodes
    WITH DISTINCT {', '.join(with_query)}, pathNodes, [node IN pathNodes | node.uid] + [x IN pathNodes | head([(x)-[:IS_A]->(neighbor) | neighbor.name])] as combinations
    UNWIND pathNodes AS pathNode 
    CALL apoc.case([
        pathNode:{ONTOMAPPER["EMMOMatter"]}, 'OPTIONAL MATCH (onto)<-[:IS_A]-(pathNode)-[node_p:HAS_PROPERTY]->(property:Quantity)-[:IS_A]->(property_label:EMMOQuantity) RETURN DISTINCT [pathNode.uid, node_p.float_value, onto.name + "_" + property_label.name] as node_info',
        pathNode:{ONTOMAPPER["EMMOProcess"]}, 'OPTIONAL MATCH (onto)<-[:IS_A]-(pathNode)-[node_p:HAS_PARAMETER]->(property:Quantity)-[:IS_A]->(property_label:EMMOQuantity) RETURN DISTINCT [pathNode.uid, node_p.float_value, onto.name + "_" + property_label.name] as node_info'
    ])
    YIELD value as node_info
    WITH DISTINCT collect(DISTINCT node_info["node_info"]) as node_info, combinations
    RETURN DISTINCT apoc.coll.toSet(collect(DISTINCT combinations)) as combinations, apoc.coll.toSet(apoc.coll.flatten(collect(DISTINCT node_info))) as metadata"""

        # print(query)
        # return query
        node_list = self.query_list
        params = {"node_list": node_list}
        print(query)
        return query, params





    def build_result(self):

        # if self.count:
        #     return self.db_results[0][0]
        return create_table_structure(self.db_result)

    def build_results_for_report(self):
        # Dynamic extraction
        result = create_table_structure(self.db_result)
        return result.values.tolist(), result.columns


    def build_extra_reports(self):
        pass


def main():
    pass

# Django-related imports only when the script is run directly
if __name__ == "__main__":
    import django
    from django.template.loader import render_to_string
    from django.conf import settings

    from dbcommunication.ai.searchEmbeddings import EmbeddingSearch
    from matching.matcher import Matcher
    from matgraph.models.ontology import EMMOMatter, EMMOProcess

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mat2devplatform.settings')

    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the current working directory to the project root directory
    os.chdir(project_root)

    load_dotenv()

    # Setup Django
    django.setup()
    main()
