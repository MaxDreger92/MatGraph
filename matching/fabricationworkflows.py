import os

import pandas as pd
from dotenv import load_dotenv

from matching.matcher import Matcher
from matgraph.models.ontology import EMMOMatter, EMMOProcess, EMMOQuantity


def create_table_structure(data):
    # Extract combinations and attributes
    combinations = data[0][0]
    attributes = data[0][1]

    # Check if combinations list is empty
    if len(combinations) == 0:
        # Create a DataFrame with the message and save it to a CSV file
        no_data_df = pd.DataFrame({"Message": ["No workflows found for your query"]})
        no_data_df.to_csv("output_filename.csv", index=False)
        print("No workflows found for your query.")
        return no_data_df

    print(f"Number of combinations: {len(combinations)}")

    # Dynamically generate column names based on the longest combination
    max_len = max(map(len, combinations))
    half_len = max_len // 2  # We assume max_len is always even for this to work

    uid_columns = [f"UID_{i + 1}" for i in range(half_len)]
    name_columns = [f"name_{i + 1}" for i in range(half_len)]

    columns = uid_columns + name_columns
    print(columns)
    print(combinations[0])

    # Convert combinations into a DataFrame
    df_combinations = pd.DataFrame(combinations, columns=columns).fillna("N/A")
    df_combinations = df_combinations.drop_duplicates(subset=columns)

    # Convert attributes into a DataFrame
    df_attributes_raw = pd.DataFrame(attributes, columns=["UID", "Value", "Attribute"]).fillna("N/A")
    df_attributes = df_attributes_raw.drop_duplicates(subset=["UID", "Attribute"])

    # Pivot the attributes dataframe
    df_pivoted = df_attributes.pivot(index="UID", columns="Attribute", values="Value").reset_index()
    df_pivoted["UID"] = df_pivoted["UID"].fillna("N/A")
    df_combinations = df_combinations.fillna("N/A")

    # Iteratively merge with the combinations dataframe on each UID
    for i, column in enumerate(columns):
        merged = pd.merge(df_combinations, df_pivoted, how="left", left_on=column, right_on="UID", suffixes=("", f"_y{i + 1}"))
        # Drop the unnecessary UID column (which came from df_pivoted)
        merged.drop("UID", axis=1, inplace=True)
        df_combinations = merged

    # Drop columns that have only NaNs
    final_df = df_combinations.dropna(axis=1, how="all")

    # Drop all columns that contain the string 'UID'
    final_df = final_df[final_df.columns.drop(list(final_df.filter(regex="UID")))]

    # Save the final DataFrame to a CSV file
    final_df.to_csv("output_filename.csv", index=False)

    return final_df


# TODO implement filtering for values!
QUERY_BY_VALUE = """"""

ONTOMAPPER = {"matter": "EMMOMatter", "manufacturing": "EMMOProcess", "measurement": "EMMOProcess", "property": "EMMOQuantity", "parameter": "EMMOQuantity"}

RELAMAPPER = {"IS_MANUFACTURING_INPUT": "IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT", "IS_MANUFACTURING_OUTPUT": "IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT", "HAS_PARAMETER": "HAS_PARAMETER", "HAS_PROPERTY": "HAS_PROPERTY"}

RELATIONSHIP_MAP = {
    ("matter", "manufacturing"): "IS_MANUFACTURING_INPUT",
    ("manufacturing", "matter"): "IS_MANUFACTURING_OUTPUT",
    ("matter", "measurement"): "IS_MEASUREMENT_INPUT",
    ("matter", "property"): "HAS_PROPERTY",
    ("manufacturing", "parameter"): "HAS_PARAMETER",
    ("measurement", "parameter"): "HAS_PARAMETER",
    ("measurement", "property"): "HAS_MEASUREMENT_OUTPUT",
    ("manufacturing", "metadata"): "HAS_METADATA",
    ("measurement", "metadata"): "HAS_METADATA",
    ("matter", "matter"): "HAS_PART",
    ("manufacturing", "manufacturing"): "HAS_PART",
    ("measurement", "measurement"): "HAS_PART",
}

OPERATOR_MAPPING = {"=": "=", "!=": "<>", ">": ">", ">=": ">=", "<": "<", "<=": "<="}


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

        self.query_list = [{**node, "uid": self._get_uid(node)} for node in workflow_list["nodes"]]
        self.relationships = workflow_list["relationships"]
        self.count = count
        super().__init__(**kwargs)

    @staticmethod
    def pick_attr_value(field):
        """Normalizes dicts, lists, scalars → returns the first usable value."""
        if isinstance(field, list):
            for item in field:
                if isinstance(item, dict) and "value" in item:
                    return item["value"]
            return field[0] if field else None
        if isinstance(field, dict):
            return field.get("value")
        return field

    @staticmethod
    def pick_attr_operator(field, default=None):
        """
        Pull an 'operator' alongside a value field that may be dict or list-of-dicts.
        Returns e.g. "<=" or the provided default.
        """
        if isinstance(field, list):
            for item in field:
                if isinstance(item, dict) and "operator" in item:
                    return item["operator"]
            return default
        if isinstance(field, dict):
            return field.get("operator", default)
        return default

    def _get_uid(self, node):
        """Resolve the UID based on node label + normalized name."""
        name_val = self.pick_attr_value(node.get("attributes", {}).get("name"))
        label = ONTOMAPPER.get(node.get("label"))

        if label == "EMMOMatter":
            return EMMOMatter.nodes.get_by_string(string=name_val, limit=10)[0].uid if name_val else None
        if label == "EMMOProcess":
            return EMMOProcess.nodes.get_by_string(string=name_val, limit=10)[0].uid if name_val else None
        if label == "EMMOQuantity":
            return EMMOQuantity.nodes.get_by_string(string=name_val, limit=10)[0].uid if name_val else None
        return "nope"

    def _build_ontology_query(self, node):
        node_id, label = node["id"], node["label"]
        onto = ONTOMAPPER.get(label)
        uid = node.get("uid")
        if not onto or not uid:
            return f"(onto_{node_id})"
        return f"(onto_{node_id}: {onto} {{uid: '{uid}'}})"

    def _build_tree_query(self, node_id, label):
        onto = ONTOMAPPER.get(label)
        if not onto:
            return f""
        return f"""CALL {{
            WITH onto_{node_id}
            OPTIONAL MATCH (onto_{node_id})<-[:EMMO__IS_A*..]-(tree_onto_{node_id}:{onto})
            RETURN collect(DISTINCT tree_onto_{node_id}) + collect(DISTINCT onto_{node_id}) AS combined_{node_id}
        }}
        """

    def _build_find_nodes_query(self, node_id, label, attributes):
        label = (label or "").capitalize()
        where_clause = ""
        if label in ("Property", "Parameter"):
            val_field = attributes.get("value") if isinstance(attributes, dict) else None
            value = self.pick_attr_value(val_field)
            op_sym = self.pick_attr_operator(val_field, default="=")
            operator = OPERATOR_MAPPING.get(op_sym, "=")

            if value is not None:
                where_clause = f"WHERE toFloat(node_{node_id}.value) {operator} toFloat({value})"

        return f"""CALL {{
            WITH combined_{node_id}
            UNWIND combined_{node_id} AS full_onto_{node_id}
            MATCH (full_onto_{node_id})<-[:IS_A]-(node_{node_id}:{label})
            {where_clause}
            RETURN collect(DISTINCT node_{node_id}) AS nodes_{node_id}
        }}
        """

    def _build_path_queries(self):
        path_queries = []
        for i, rel in enumerate(self.relationships):
            source, target = rel["connection"]
            rel_type = rel["rel_type"]
            path_queries.append(self._build_single_path_query(source, target, rel_type, i))
        return path_queries

    def _build_path_conditions(self, paths, uid_paths, xid_paths, relationships):
        path_conditions = []
        return_statements = []
        idx_list = []

        for idx, rel in enumerate(relationships):
            idx_var = f"idx{idx}"
            idx_list.append(idx_var)

            source, target = rel["connection"]
            uid_path = f"uids_path_{source}_{target}"
            path = f"path_{source}_{target}"
            return_statements.append(f"nodes({path}[{idx_var}])")

            for idx2, rel2 in enumerate(relationships):
                if idx == idx2:
                    continue
                source2, target2 = rel2["connection"]
                uid_path2 = f"uids_path_{source2}_{target2}"

                if source == source2:
                    path_conditions.append(f"{uid_path}[{idx_var}][0] = {uid_path2}[idx{idx2}][0]")
                if target == target2:
                    path_conditions.append(f"{uid_path}[{idx_var}][-1] = {uid_path2}[idx{idx2}][-1]")
                if source == target2:
                    path_conditions.append(f"{uid_path}[{idx_var}][0] = {uid_path2}[idx{idx2}][-1]")

        if len(relationships) == 1:
            path = paths[0]
            return f"""
            CALL {{
                WITH {path}
                UNWIND {path} AS p
                WITH collect(DISTINCT nodes(p)) AS node_lists
                RETURN apoc.coll.toSet(apoc.coll.flatten(node_lists)) AS pathNodes
            }}
            """

        path_condition = " AND ".join(path_conditions)
        return_expr = "[" + ", ".join(idx_list) + "]"
        unwinds = " ".join([f"UNWIND range(0, size({uid_path})-1) AS idx{i}" for i, uid_path in enumerate(uid_paths)])
        where_clause = f"WHERE {path_condition}" if path_condition else ""

        return f"""
        CALL {{
            WITH {", ".join(uid_paths)}
            {unwinds}
            WITH {", ".join(idx_list + uid_paths)}
            {where_clause}
            RETURN collect(DISTINCT {return_expr}) AS idxs
        }}

        CALL {{
            WITH idxs, {", ".join(paths)}
            UNWIND idxs AS local_idx
            RETURN apoc.coll.toSet(apoc.coll.flatten([{", ".join([f"nodes({path}[local_idx[{i}]])" for i, path in enumerate(paths)])}])) AS pathNodes
        }}
        """

    def _build_single_path_query(self, source, target, rel_type, index):
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

    def _build_path_queries_and_conditions(self):
        paths, uid_paths, xid_paths, path_combinations = [], [], [], []
        path_queries = []

        node_labels = {node["id"]: node.get("label") for node in self.query_list}

        for i, rel in enumerate(self.relationships):
            source, target = rel["connection"]
            rel_type = rel.get("rel_type")
            if rel_type is None:
                source_label = node_labels.get(source)
                target_label = node_labels.get(target)
                rel_type = RELATIONSHIP_MAP.get((source_label, target_label))
                if rel_type is None:
                    raise ValueError(f"Cannot determine rel_type for relationship between {source_label} → {target_label}")
            path = f"path_{source}_{target}"
            uid_path = f"uids_path_{source}_{target}"
            xid_path = f"idx_uids_path_{source}_{target}"

            paths.append(path)
            uid_paths.append(uid_path)
            xid_paths.append(xid_path)
            path_combinations.append(f"nodes({path})[idx{i}]")

            path_queries.append(self._build_single_path_query(source, target, rel_type, i))

        path_connector = self._build_path_conditions(paths, uid_paths, xid_paths, self.relationships)
        return "\n".join(path_queries) + "\n" + path_connector

    def _build_results(self):
        return f"""
        WITH DISTINCT
        pathNodes,
        [NODE IN pathNodes | NODE.uid] + [x IN pathNodes | head([(x)-[:IS_A]->(neighbor) | neighbor.name])] AS combinations
        UNWIND pathNodes AS pathNode
        CALL apoc.case([
        pathNode:Matter,
        'OPTIONAL MATCH (onto)<-[:IS_A]-(pathNode)-[node_p:HAS_PROPERTY]->(property:Property)-[:IS_A]->(property_label:EMMOQuantity) RETURN [pathNode.uid, property.value, onto.name + "_" + property.name] as node_info',

        pathNode:Process,
        'OPTIONAL MATCH (onto)<-[:IS_A]-(pathNode)-[node_p:HAS_PARAMETER]->(property:Parameter)-[:IS_A]->(property_label:EMMOQuantity) RETURN [pathNode.uid, property.value, onto.name + "_" + property_label.name + "_" + property.name] as node_info'
        ])
        YIELD value AS node_info
        WITH collect(node_info['node_info']) AS node_info, combinations
        RETURN DISTINCT apoc.coll.toSet(collect(DISTINCT combinations)) AS combinations,
        apoc.coll.toSet(apoc.coll.flatten(collect(node_info))) AS metadata
        """

        # Assuming _build_single_path_query remains unchanged

    def build_query(self):
        ontology_queries = [self._build_ontology_query(node) for node in self.query_list]
        tree_queries = [self._build_tree_query(node["id"], node["label"]) for node in self.query_list]
        find_nodes_queries = [self._build_find_nodes_query(node["id"], node["label"], node["attributes"]) for node in self.query_list]
        path_queries_and_conditions = self._build_path_queries_and_conditions()
        prepare_results = self._build_results()

        # Combining all parts into a single query
        final_query = f"""MATCH {", ".join(ontology_queries)} 
        {" ".join(tree_queries + find_nodes_queries + [path_queries_and_conditions] + [prepare_results])}
        """
        print(final_query)
        return final_query, {}

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
