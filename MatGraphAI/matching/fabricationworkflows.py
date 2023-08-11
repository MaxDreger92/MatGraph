from collections import defaultdict
from pprint import pprint
from uuid import UUID
import os

import pandas as pd


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

    print(final_df)
    print(f"DF size: {final_df.shape[0]}")
    final_df.to_csv('output_filename.csv', index=False)

    return final_df


# TODO implement filtering for values!
QUERY_BY_VALUE = """"""
from matching.matcher import Matcher
from dbcommunication.ai.searchEmbeddings import EmbeddingSearch
from matgraph.models.ontology import *

ONTOMAPPER = {"EMMOMatter": "Matter",
              "EMMOProcess": "Process",
                "EMMOQuantity": "Quantity"}

RELAMAPPER = {"IS_MANUFACTURING_INPUT": "IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT",
              "IS_MANUFACTURING_OUTPUT": "IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT",
              "HAS_PARAMETER": "HAS_PARAMETER"}


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
        materials_search = EmbeddingSearch(EMMOMatter)
        process_search = EmbeddingSearch(EMMOProcess)
        quantity_search = EmbeddingSearch(EMMOQuantity)
        self.query_list = [
            {
                **node,
                'uid': materials_search.find_string(node['name']) if node['type'] == 'EMMOMatter' else
                process_search.find_string(node['name']) if node['type'] == 'EMMOProcess' else
                quantity_search.find_string(node['name']) if node['type'] == 'EMMOQuantity' else 'nope'
            }
            for node in workflow_list
        ]
        pprint(self.query_list)
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

        for node in self.query_list:
            where_query.append(f""" onto_{node['id']}.uid = '{node['uid']}'""")
            with_query.append(f""" {node['id']}""")
            if node['type'] == 'EMMOQuantity':
                match_query.append(f"""(onto_{node['id']}:{node['type']})<-[:IS_A]-({node['id']}:{ONTOMAPPER[node['type']]})<-[rel_{node['id']}:HAS_PARAMETER]-()""")
                where_query.append(f""" rel_{node['id']}.float_value {node['operator']} {node['value']}""")
            else:
                match_query.append(f"""(onto_{node['id']}:{node['type']} {{uid: '{node['uid']}'}})<-[:IS_A]-({node['id']}:{ONTOMAPPER[node['type']]})""")


        # Constructing the relationship paths                m
            for rel in node["relationships"]:
                if rel['connection'][0] == node['id']:
                    relationship_query.append(f"""path_{rel['connection'][0]}_{rel['connection'][1]} = (({rel['connection'][0]})-[:{RELAMAPPER[rel['rel_type']]}*..5]->({rel['connection'][1]}))""")
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
    MATCH {', '.join(match_query)}
    WHERE {' AND '.join(where_query)}
    WITH {', '.join(with_query)}
    MATCH {' MATCH '.join(relationship_query)}
    WHERE {' AND '.join(conditions)}
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

        node_list = self.query_list
        params = {"node_list": node_list}
        print(query)
        return query, params





    def build_result(self):

        if self.count:
            return self.db_results[0][0]
        pass

    def build_results_for_report(self):
        # Dynamic extraction
        print("RESULT")
        pprint(create_table_structure(self.db_result))
        return self.db_result[0][0], self.db_columns


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
