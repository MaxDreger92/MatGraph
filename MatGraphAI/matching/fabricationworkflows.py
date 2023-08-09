from pprint import pprint
from uuid import UUID
import os

import pandas as pd


def create_table_structure(data):
    # Convert combinations list to a DataFrame
    combinations = data[0][0]
    attributes = data[0][1]
    print(f"Number of combinations: {len(combinations)}")

    # Convert combinations into a DataFrame
    df_combinations = pd.DataFrame(combinations, columns=['UID1', 'UID2'])

    # Convert attributes into a DataFrame
    df_attributes = pd.DataFrame(attributes, columns=['UID', 'Value', 'Attribute'])

    # Pivot the attributes dataframe
    df_pivoted = df_attributes.pivot(index='UID', columns='Attribute', values='Value').reset_index()

    # Merge with combinations dataframe on UID1
    merged_1 = pd.merge(df_combinations, df_pivoted, how='left', left_on='UID1', right_on='UID', suffixes=('', '_y'))
    # Drop the unnecessary UID column (which came from df_pivoted)
    merged_1.drop('UID', axis=1, inplace=True)

    # Now, merge merged_1 with df_pivoted on UID2
    final_df = pd.merge(merged_1, df_pivoted, how='left', left_on='UID2', right_on='UID', suffixes=('', '_y2'))
    # Drop the unnecessary UID column (which came from df_pivoted)
    final_df.drop('UID', axis=1, inplace=True)

    # Drop columns that have only NaNs
    final_df = final_df.dropna(axis=1, how='all')

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
              "IS_MANUFACTURING_OUTPUT": "IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT"}


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
        with_query = []
        filter_node_query = []
        filter_relation_query = []
        optional_match_query = []
        return_query = []
        # Create a list to hold uid pairs
        pair_list = []
        info_list = []
        uid_list = []

        for node in self.query_list:
            # Constructing the main MATCH and WHERE clauses
            match_query.append(f"""(onto_{node['id']}:{node['type']} {{uid: '{node['uid']}'}})<-[:IS_A]-({node['id']}:{ONTOMAPPER[node['type']]})""")
            filter_node_query.append(f"""onto_{node['id']}.uid = '{node['uid']}'""")

            # Adding the node uid to pair list
            pair_list.append(f"{node['id']}.uid")

            # Constructing the OPTIONAL MATCH based on the node type
            if node["type"] == "EMMOMatter":
                optional_match_query.append(f"""
                CALL {{
                with {node['id']}
                OPTIONAL MATCH ({node['id']})-[{node['id']}_p:HAS_PROPERTY]->({node['id']}_property:Quantity)-[:IS_A]->({node['id']}_property_label:EMMOQuantity)
                RETURN DISTINCT [{node['id']}.uid, {node['id']}_p.float_value, {node['id']}_property_label.name] as {node['id']}_info
                }}""")
            elif node["type"] == "EMMOProcess":
                optional_match_query.append(f"""
                CALL {{
                with {node['id']}
                OPTIONAL MATCH ({node['id']})-[{node['id']}_p:HAS_PARAMETER]->({node['id']}_parameter:Quantity)-[:IS_A]->({node['id']}_parameter_label:EMMOQuantity)
                RETURN DISTINCT [{node['id']}.uid, {node['id']}_p.float_value, {node['id']}_parameter_label.name] as {node['id']}_info
                }}""")
            info_list.append(f"""collect({node['id']}_info)""")
            uid_list.append(f"""{node['id']}.uid""")
            with_query.append(f"""{node['id']}""")
            for rel in node["relationships"]:
                if rel['direct']:
                    filter_relation_query.append(f"""({rel['connection'][0]})-[:{rel['rel_type']}]->({rel['connection'][1]})""")
                else:
                    filter_relation_query.append(f"""({rel['connection'][0]})-[:{RELAMAPPER[rel['rel_type']]}*..]->({rel['connection'][1]})""")

        return_query.append(f"""[{", ".join(pair_list)}]  as pairs""")

        # Construct the main query parts
        query = f"""MATCH {', '.join(match_query)} 
            WHERE {' AND '.join(filter_node_query)}{' AND ' + ' AND '.join(filter_relation_query) if filter_relation_query else ''} 
            WITH DISTINCT {', '.join(with_query)}
            {' '.join(optional_match_query)}
            RETURN DISTINCT collect(DISTINCT [{', '.join(uid_list)}]) as combinations, apoc.coll.union({', '.join(info_list)}) as metadata"""

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
