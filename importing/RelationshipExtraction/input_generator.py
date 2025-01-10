import csv
import json
import re
from collections import defaultdict
from pprint import pprint


def csv_to_json(file_name):
    """
    Convert rows of a CSV file labeled "node_label", "node_attribute", and "node_id" into a JSON structure,
    combining nodes with the same node_id.

    Parameters:
    - file_name (str): Path to the CSV file.

    Returns:
    - str: Pretty-printed JSON representation of the combined nodes defined in the labeled rows in the CSV.
    """

    # Helper function to parse attributes
    def parse_attributes(attr_str, header, second_row, index):
        matches = re.findall(r'(\w+)', attr_str)
        match_dict = {
            matches[i - 1]: {"position": [index, matches[i]], "data": header if matches[i] == "header" else second_row}
            for i in range(1, len(matches), 2)
        }
        return match_dict

    node_data = defaultdict(list)

    with open(file_name, 'r') as f:
        csv_reader = csv.reader(f)
        header, second_row = next(csv_reader)[1:], next(csv_reader)[1:]

        # Extracting the rows based on the labels in the first column
        for label, *values in csv_reader:
            node_data[label].extend(values)

        # Create nodes using a list comprehension
        nodes = [
            {
                "node_id": node_id,
                "label": label,
                "attributes": parse_attributes(attribute, heading, second_row_cell, index)
            }
            for node_id, label, attribute, heading, second_row_cell, index in
            zip(node_data["node_id"], node_data["node_label"], node_data["node_attribute"], header, second_row, range(len(node_data["node_id"])))
        ]

    # Group nodes by node_id and combine nodes with the same node_id
    grouped_nodes = defaultdict(list)
    for node in nodes:
        grouped_nodes[node["node_id"]].append(node)

    combined_nodes = []
    for node_id, group in grouped_nodes.items():
        combined_attributes = defaultdict(list)
        for node in group:
            for attr_key, attr_value in node["attributes"].items():
                combined_attributes[attr_key].append(attr_value)

        combined_nodes.append({
            "node_id": node_id,
            "label": ", ".join(list(dict.fromkeys([node["label"] for node in group]))),
            "attributes": combined_attributes
        })
    for node in combined_nodes:
        if node['label'] == '' or node['attributes'] == {} or node['node_id'] == '':
            combined_nodes.remove(node)

    return json.dumps({"nodes": combined_nodes, "headers": header}, indent=4)


def extract_data(json_data_str, label):
    json_data = json.loads(str(json_data_str).replace('\'', '"'))
    # Parse the JSON data
    nodes = json_data.get('nodes', [])

    # Extract manufacturing data
    label_data = [node for node in nodes if node.get('label') == label]

    return label_data

def generate_strings(label_one_data, label_two_data, label_one, label_two, rel):
    if not label_one_data or not label_two_data:
        return []

    def get_attributes(node):
        attributes_str = ""
        for key, value in node["attributes"].items():
            attributes_str += f"with {key}(s) "
            for attr in node["attributes"][key]:
                attributes_str += f"""{attr["data"]}, """
        return attributes_str

    # Create the desired output
    output = []
    index = 1
    for node_one in label_one_data:
        node_one_attributes = get_attributes(node_one)
        for node_two in label_two_data:
            node_two_attributes = get_attributes(node_two)
            output.append(f'{str(index)}. {label_one} {node_one_attributes} {rel} {label_two} {node_two_attributes}')
            index += 1

    return output


def process_input(json_data_str, label_one, label_two, rel):
    json_data = json.loads(json_data_str)
    label_one_data, label_two_data = extract_data(json_data, label_one, label_two)
    return generate_strings(label_one_data, label_two_data, label_one, label_two, rel)


def remove_key(json_obj, key_to_remove):
    if isinstance(json_obj, dict):
        if key_to_remove in json_obj:
            del json_obj[key_to_remove]
        for key in json_obj:
            remove_key(json_obj[key], key_to_remove)
    elif isinstance(json_obj, list):
        for item in json_obj:
            remove_key(item, key_to_remove)
    return json_obj


def extract_values_from_list_of_dicts(data: list) -> list:
    """
    Extract all values from a list of dictionaries and return them in a single list.

    Args:
        data (list): A list of dictionaries.

    Returns:
        list: A single list containing all the values from the input list of dictionaries.
    """
    return [value for dct in data for value in dct.values()]


def flatten_dict(dict):
    for key in dict.keys():
        att_list = extract_values_from_list_of_dicts(dict[key])
        dict[key] = []
        [dict[key].append(item) for item in att_list if item not in dict[key]]
    return dict

def flatten_json(json_obj):
    return json_obj


def prepare_lists(input_json, label1, label2):
    label_one_data = [flatten_json(remove_key(extract_data(input_json, label), "position")) for label in label1]
    label_two_data = [flatten_json(remove_key(extract_data(input_json, label), "position")) for label in label2]

    label_two_data = [item for sublist in label_two_data for item in sublist]
    label_one_data = [item for sublist in label_one_data for item in sublist]

    return label_one_data, label_two_data


def get_node_ids(list1, list2):
    return [*[item['node_id'] for item in list1], *[item['node_id'] for item in list2]]


def main():
    file_name = "../../data/materials.csv"
    input_json = (csv_to_json(file_name))
    list1, list2 = prepare_lists(input_json, "matter", "manufacturing")
    print(list2)
    print(get_node_ids(list1, list2))


if __name__ == "__main__":
    main()
