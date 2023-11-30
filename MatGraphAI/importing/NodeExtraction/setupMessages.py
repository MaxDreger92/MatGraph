# CONTEXT_GENERATION_MESSAGE_NEW = [{"role": "system",
#                                "content": """
# You are a helpful knowledge graph expert with deep knowledge in materials science. You exist to extract nodes and their attributes from the input data.
# You have a great understanding of the table structure and the context of the data. You are able to precisely extract nodes and their attributes from the input data.
#
#
# The data input is a list of dictionaries that contains:
# - the header of each column
# - a sample column
# - the attribute_type that needs to be extracted
#
# The nodes you need to separately are:
# - Materials
# - Components
# - Devices
# - Intermediates
# - Products
# - Chemicals
# - Functional Units
# - Parts
# etc.
#
#
# You Follow these steps to extract the nodes
#
# 1. Analyse the given attributes given in the input table.
#     - use "name" attributes to infer which nodes can be extracted from the table
#     - sometimes names can describe the one and the same nodes in that case the node has several names
#     - to create a knowledge graph it is important that all materials/components/devices/products are extracted as nodes that
#     are mentioned in the table
#     - do not aggregate nodes that are not the same, only aggregate them if they represent the same real-world entity
#     Example: "ionomer", "solvent" "EthOH" "Pt", "CatalystInk" should form 4 nodes with the names ["ionomer"], ["solvent", "EthOH"], ["Pt"], ["CatalystInk"]
#     Reason: "Ethanol" is a "solvent" therefore they are the same node. "ionomer", ["solvent", "EthOH"], "Pt" are part of "CatalystInk", they are used to form the "CatalystInk"
#     therefore they all need to be separate nodes different nodes.
#
#
# 2. Aggreggate the given attributes to nodes
#     - building on the nodes that you inferred from the names you assign attributes
#     - each distiguishable material/chemical/component/device/product needs to be extracted as a separate node
#
#
# 3. Add additional attributes/nodes that can be inferred from the context
#     - use your materials science knowledge to infer additional attributes/nodes from the context (sometimes a node can be inferred from an identifier
#     or from the context)
#     - each node needs to have at least one name so if a name is missing add it to the node
#
#
# 4. Create a list of dictionaries that contains the nodes and their attributes following the given format:
#
# You only generate output that strictly follows the following format:
# [
# {
#     "description": "Schema for Output Node List in Knowledge Graph",
#     "type": "array",
#     "items": {
#         "type": "object",
#         "properties": {
#             "name": {
#                 "description": "Names of the node with their corresponding indexes or None.",
#                 "type": "array",
#                 "items": {
#                     "type": "array",
#                     "items": [
#                         {"type": "string"},
#                     {"type": ["integer", "null"]]}
#                     ],
#                     "minItems": 2,
#                     "maxItems": 2
#                 }
#             },
#             "identifier": {
#                 "description": "Unique identifier for the node with its index or None.",
#                 "type": "array",
#                 "items": [
#                     {"type": "string"},
#                     {"type": ["integer", "null"]]}
#                 ],
#                 "minItems": 2,
#                 "maxItems": 2
#             },
#             "concentration": {
#                 "description": "Concentration value associated with the node with its index or None.",
#                 "type": "array",
#                 "items": [
#                     {"type": "string"},
#                     {"type": ["integer", "null"]]}
#                 ],
#                 "minItems": 2,
#                 "maxItems": 2
#             },
#             "ratio": {
#                 "description": "Ratio value associated with the node with its index or None.",
#                 "type": "array",
#                 "items": [
#                     {"type": "string"},
#                     {"type": ["integer", "null"]]}
#                 ],
#                 "minItems": 2,
#                 "maxItems": 2
#             },
#             "batch number": {
#                 "description": "Batch number associated with the node with its index or None.",
#                 "type": "array",
#                 "items": [
#                     {"type": "string"},
#                     {"type": ["integer", "null"]]}
#                 ],
#                 "minItems": 2,
#                 "maxItems": 2
#             }
#         },
#         "required": ["name"]
#     }
# }
# ]
#
# ALWAYS REMEMBER:
# - the final output needs to contain all nodes that can be extracted from the context and the table
# - do not aggregate nodes by their name that if the names are describing their composition
# ("Catalyst", "CatalystLayer" are different nodes as the "Catalyst" is part of the "CatalystLayer")
# """},
# {"role": "user",
#                     "content": f"""
# Context: Catalyst Fabrication
#
# Headers/Row: [
# {{"column_header": "id", "column_value": "CT-1001", "attribute_type": "identifier", "index": 1}},
# {{"column_header": "MaterialA", "column_value": "Pt", "attribute_type": "name", "index": 2}},
# {{"column_header": "MaterialB", "column_value": "C", "attribute_type": "name", "index": 3}},
# {{"column_header": "MaterialC", "column_value": "Pd", "attribute_type": "name", "index": 4}},
# {{"column_header": "ratioA", "column_value": "50", "attribute_type": "ratio", "index": 5}},
# {{"column_header": "ratioB", "column_value": "30", "attribute_type": "ratio", "index": 6}},
# {{"column_header": "ratioC", "column_value": "20", "attribute_type": "ratio", "index": 7}},
#
#
#                     """},
# {"role": "system",
#                     "content": f"""
#
# To process the given input and achieve the specified output, let's follow the instructions:
#
#     1. Analyze Attributes in the Input Table:
#         Identify nodes and their attributes based on the "name" and "attribute_type" in the input.
#         For example, "MaterialA", "MaterialB", and "MaterialC" are identified as distinct nodes based on their names "Pt", "C", and "Pd".
#
#     2. Attribute Aggregation to Nodes:
#         based on the "names" given in the input we can extract the following nodes:
#         - MaterialA
#             name: Pt, index: 2
#
#         - MaterialB
#             name: C, index: 3
#
#         - MaterialC
#             name: Pd, index: 4
#
#         Furthermore, we can assign the following attributes to the nodes:
#         - MaterialA
#             name: Pt, index: 2
#             ratio: 50, index: 5
#
#         - MaterialB
#             name: C, index: 3
#             ratio: 30, index: 6
#
#         - MaterialC
#             name: Pd, index: 4
#             ratio: 20, index: 7
#
#
#     3. Infer Additional Attributes or Nodes:
#         The context and the identifier "CT-1001" can be used to infer the following nodes:
#         - Catalyst
#             name: Catalyst
#             identifier: CT-1001
#
#     4. Construct the Output List:
#         Final Output:
#
# [{{"name": [["Catalyst", None]], "identifier": ["CT-1001", 1]}},
# {{"name": [["Pt", 2]], "ratio": ["50", 5]}},
# {{"name": [["C", 3]], "ratio": ["30", 6]}},
# {{"name": [["Pd", 4]], "ratio": ["20", 7]}}]
# """},
#
#
#                               ]

CONTEXT_GENERATION_MESSAGE = [{"role": "system",
                               "content": """
You are a helpful knowldge graph expert with deep knowledge in materials science and you exist to extract nodes and their attributes from the input data.

You will receive the following input list that contains:
- the header of each column
- a sample column
- the attribute_type that needs to be extracted
- the column index

Further, you get the context of the data and the table structure.

You always need to follow these steps to successfully extract the nodes:

1. Explicit Node Extraction from Table Data:
    1.1 Check if the table contains names that describe the real-world object (as materials/components are often either described by their composition or their function) 
    and gather them together for this you need to use your knowledge of materials science and check the table structure as attributes describing the same node might be
    in columns that are close to each other. Use the column headers to infer which names might belong to the same node and
    which names describe different nodes.
    Examples: 
        - "KOH", "Base" might be "name" attributes of the same node as "KOH" is a "Base"
        - "Catalyst Layer" "Pt" "C" are different nodes as the "Pt" and "C" are "Catalyst Layer" materials 
    1.2 Create a list of nodes that are explicitly mentioned in the table 
    Output: List of nodes with names 
    ( e.g. [{"name": [["KOH", 2], ["Base", 3]]}, {"name": [["Electrode", 4]]}] )

2. Node Identification from Context and Structure:
    2.1. Analyze the table structure and the context of the data to identify all nodes. (e.g., if the context is "Battery Fabrication" and the table contains a "Run ID" 
    column then the node "Battery" can be inferred as the ID is used to identify the battery). Use your domain knowledge to make sure you extrct all nodes
    and the you aggregate the correct names into the right nodes.
    Output: List of all nodes with names
        ( e.g. [{"name": [["KOH", 2], ["Base", 3]]}, {"name": [["Electrode", 4]]}]}, {"name": [["Battery", inferred]]}] )

3. Attribute Assignment:
    Assign attributes to nodes based on the input data, including the column index for each attribute.
    Add "inferred" for attributes not directly mentioned in the table but deduced from context.

    3.1. Name Assignment:
        3.1.1 Check all nodes in your node list and check if "names" can be assigned to them using the context or its column header.

    3.2. Identifier Assignment:
        3.2.1   Check all "identifier" attributes in your input list and assign them to the right nodes (use the context and the table structure to infer the right node).
                Each node can only have zero or one identifier.
              
    3.3. Concentration Assignment:
        3.3.1   Check all "concentration" attributes in your input list and assign them to the right nodes (use the context and the table structure to infer the right node).
                Each node can only have zero or one concentration.
                Example: - The concentration "10" and the nodes "Membrane" and "KOH" let you infer that the concentration belongs to the "KOH" as
                a membrane cannot have a concentration.
              
    3.4. Ratio Assignment:
        3.4.1   Check all "ratio" attributes in your input list and assign them to the right nodes (use the context and the table structure to infer the right node).
                Each node can only have zero or one ratio.
                Example: - The ratios "10" "50" and "40" and the nodes "Pt", "C", "Pd" and "CatalystPowder" let you infer that the ratios belong to the "Pt", "C", "Pd" as
                the "catalyst powder" is fabricated by mixing the "Pt", "C", "Pd" in the given ratios for which three ratios are given 
                the right assignment needs to be done by analyzing the table structure and the context.
              

    3.5. Batch Number Assignment:
        3.5.1   Check all "batch number" attributes in your input list and assign them to the right nodes (use the context and the table structure to infer the right node).
    
4. Create a list of dictionaries that contains the nodes and their attributes following the given format:

Nodes:

[{{"name": [["Cat", "inferred"],["PdC", 2]], "identifier": ["1233495", 1], "batch number": ["0005", 3]}},
{{"name": [["Solvent", "5"],["EtOh", 2]], "identifier": ["ION-2002", 4], "concentration": ["10%", 6]}},
{{"name": [["Anode", "8"]], "identifier": ["An-6006", 16]}},
{{"name": [["Cathode", "9"],["110", 0]]}},
{{"name": [["Electrolyte", "inferred"],["E3", 13]]}}]

"""},
                              {"role": "user",
                               "content": f"""
                 Context: Fuel Cell Fabrication
                 Headers/Row: [
                {{"header": "run", "row": "RN0721-28", "attribute_type": "identifier", "index": 0}},
                {{"header": "Catalyst", "row": "F50E-HT", "attribute_type": "name", "index": 2}},
                {{"header": "Catalyst", "row": "PtBased", "attribute_type": "name", "index": 2}},
                {{"header": "Catalyst Batch Number", "row": "CB-2023-001", "attribute_type": "batch number", "index": 3}},  
                {{"header": "Ionomer", "row": "AQ", "attribute_type": "name", "index": 5}},
                {{"header": "Ionomer Concentration", "row": "10%", "attribute_type": "concentration", "index": 6}},  
                {{"header": "Transfer substrate", "row": "Gore HCCM", "attribute_type": "name", "index": 10}},
                {{"header": "Membrane", "row": "MX10.15", "attribute_type": "name", "index": 12}},
                {{"header": "MEAID", "row": "MEA-5001", "attribute_type": "identifier",  "index": 13}},
                {{"header": "id", "row": "AN-5005", "attribute_type": "identifier", "index": 14}}, 
                {{"header": "Anode", "row": "Gore anode", "attribute_type": "name", "index": 15}},
                {{"header": "id", "row": "GDL-6006", "attribute_type": "identifier", "index": 16}},  
                {{"header": "GDL", "row": "HW4 B2.2", "attribute_type": "name", "index": 17}},
                {{"header": "Station", "row": "Ford", "attribute_type": "name", "index": 18}}]
                 """},

                              {"role": "system",
                               "content": f""" 

Following the instructions:

1. Explicit Node Extraction from Table Data:
    1.1 Check if the table contains names that describe the same node and gather them together:
    
    - The table contains the following names:
    - F50E-HT
    - PtBased
    - AQ
    - Gore HCCM
    - MX10.15
    - Gore anode
    - HW4 B2.2
    - Ford

   
    - We can infer the following nodes:
    - (F50E-HT, PtBased) -> Catalyst
    - (AQ) -> Ionomer
    - (Gore HCCM) -> Transfer substrate
    - (MX10.15) -> Membrane
    - (Gore anode) -> Anode
    - (HW4 B2.2) -> GDL
    
    1.2 Create a list of nodes that are explicitly mentioned in the table: 
    Output: 
    [{{"name": [["PtBased", 3],["F50E-HT", 2]}},
    {{"name": [["AQ", 5]]}},
    {{"name": [["Gore HCCM", 10]]}},
    {{"name": [["MX10.15", 12]]}},
    {{"name": [["Gore anode", 15]]}},
    {{"name": [["HW4 B2.2", 17]]}},
    {{"name": [["Ford", 18]]}}]

2. Node Identification from Context and Structure:
    2.1. Analyze the table structure and the context of the data to identify all nodes. 
    - The context is "Fuel Cell Fabrication" and the table contains a "run" column then the node "Fuel Cell" can be inferred as the ID is used to identify the fuel cell
    - Fuel Cell fabrication involves MEA fabrication, from the ID MEA-5001 we can infer the node MEA
    
    Output:
    [{{"name": [["PtBased", 3],["F50E-HT", 2]}},
    {{"name": [["AQ", 5]]}},
    {{"name": [["Gore HCCM", 10]]}},
    {{"name": [["MX10.15", 12]]}},
    {{"name": [["Gore anode", 15]]}},
    {{"name": [["HW4 B2.2", 17]]}},
    {{"name": [["Ford", 18]]}},
    {{"name": [["Fuel Cell", "inferred"]]}},
    {{"name": [["MEA", "inferred"]}}]
    
3. Attribute Assignment:
    Assign attributes to nodes based on the input data, including the column index for each attribute.
    Add "inferred" for attributes not directly mentioned in the table but deduced from context.

    3.1. Name Assignment:
        3.1.1 Check all nodes in your node list and check if "names" can be assigned to them using the context or its column header:
        - The following names can be assigned to the nodes:
        - Catalyst: Catalyst, index: "inferred"
        - Ionomer: Ionomer, index: "inferred"
        - Transfer substrate: Transfer substrate, index: "inferred"
        - Membrane: Membrane, index: "inferred"
        - Anode: Anode, index: "inferred"
        - GDL: GDL, index: "inferred"
        - Fuel Cell: Fuel Cell, index: "inferred"
        

    3.2. Identifier Assignment:
        3.2.1 Check all "identifier" attributes in your input list and assign them to the right nodes:
        - The following identifiers can be assigned to the nodes:
        - FuelCell: RN0721-28, index: 0
        - MEA: MEA-5001, index: 13
        - Anode: AN-5005, index: 14
        - GDL: GDL-6006, index: 16
        
              
    3.3. Concentration Assignment:
        3.3.1 Check all "concentration" attributes in your input list and assign them to the right nodes:
        - The following concentrations can be assigned to the nodes:
        - Ionomer: 10%, index: 6
              

    3.4. Ratio Assignment:
        3.4.1 Check all "ratio" attributes in your input list and assign them to the right nodes (use the context and the table structure to infer the right node).
              Each node can only have zero or one ratio.
        No ratio attributes are given in the input list.

    3.5. Batch Number Assignment:
        3.5.1 Check all "batch number" attributes in your input list and assign them to the right nodes (use the context and the table structure to infer the right node).
        Output:
        [{{"name": [["PtBased", 3],["F50E-HT", 2], ["Catalyst", "inferred"], ["batch number": ["CB-2023-001", 3]]}},
        {{"name": [["AQ", 5]], ["Ionomer", "inferred"], ["concentration": ["10%", 6]]}},
        {{"name": [["Gore HCCM", 10]], ["Transfer substrate", "inferred"]}},
        {{"name": [["MX10.15", 12]], ["Membrane", "inferred"]}},
        {{"name": [["Gore anode", 15]], ["Anode", "inferred"], ["identifier": ["AN-5005", 14]]}},
        {{"name": [["HW4 B2.2", 17]], ["GDL", "inferred"], ["identifier": ["GDL-6006", 16]]}},
        {{"name": [["Ford", 18]], ["Station", "inferred"]}},
        {{"name": [["Fuel Cell", "inferred"]], ["identifier": ["RN0721-28", 0]]}},
        {{"name": [["MEA", "inferred"]], ["identifier": ["MEA-5001", 13]]}}]
        
5. We create a list of dictionaries that contains the nodes and their attributes:

[{{"name": [["PtBased", 3],["F50E-HT", 2], ["Catalyst", "inferred"], ["batch number": ["CB-2023-001", 3]]}},
{{"name": [["AQ", 5]], ["Ionomer", "inferred"], ["concentration": ["10%", 6]]}},
{{"name": [["Gore HCCM", 10]], ["Transfer substrate", "inferred"]}},
{{"name": [["MX10.15", 12]], ["Membrane", "inferred"]}},
{{"name": [["Gore anode", 15]], ["Anode", "inferred"], ["identifier": ["AN-5005", 14]]}},
{{"name": [["HW4 B2.2", 17]], ["GDL", "inferred"], ["identifier": ["GDL-6006", 16]]}},
{{"name": [["Ford", 18]], ["Station", "inferred"]}},
{{"name": [["Fuel Cell", "inferred"]], ["identifier": ["RN0721-28", 0]]}},
{{"name": [["MEA", "inferred"]], ["identifier": ["MEA-5001", 13]]}}]
"""},
                              {"role": "user",
                               "content": f""" 
Context: Catalyst Fabrication

Headers/Row: [
{{"header": "id", "row": "CT-1001", "attribute_type": "identifier", "index": 1}},
{{"header": "MaterialA", "row": "Pt", "attribute_type": "name", "index": 2}},
{{"header": "MaterialB", "row": "C", "attribute_type": "name", "index": 3}},
{{"header": "MaterialC", "row": "Pd", "attribute_type": "name", "index": 4}},
{{"header": "ratioA", "row": "50", "attribute_type": "ratio", "index": 5}},
{{"header": "ratioB", "row": "30", "attribute_type": "ratio", "index": 6}},
{{"header": "ratioC", "row": "20", "attribute_type": "ratio", "index": 7}},
                    """},
                              {"role": "system",
                               "content": f"""
Following the instructions:                               

1. Explicit Node Extraction from Table Data:
    1.1 Check if the table contains names that describe the same  node and gather them together:
    - The table contains the following names:
    - Pt
    - C
    - Pd
    1.2 Create a list of nodes that are explicitly mentioned in the table
    Output:
    [{{"name": [["Pt", 2]]}},
    {{"name": [["C", 3]]}},
    {{"name": [["Pd", 4]]}}]

2. Node Identification from Context and Structure:
    2.1. Analyze the table structure and the context of the data to identify all nodes:
    - The context is "Catalyst Fabrication" and the table contains a "id" column then the node "Catalyst" can be inferred as the ID is used to identify the catalyst
    Output:
    [{{"name": [["Pt", 2]]}},
    {{"name": [["C", 3]]}},
    {{"name": [["Pd", 4]]}},
    {{"name": [["Catalyst", "inferred"]]}}]
  
3. Attribute Assignment:
    Assign attributes to nodes based on the input data, including the column index for each attribute.
    Add "inferred" for attributes not directly mentioned in the table but deduced from context.

    3.1. Name Assignment:
        3.1.1 Check all nodes in your node list and check if "names" can be assigned to them using the context or its column header:
        The following names can be assigned to the nodes:
        - Catalyst: Catalyst, index: "inferred"

    3.2. Identifier Assignment:
        3.2.1 Check all "identifier" attributes in your input list and assign them to the right nodes:
        The following identifiers can be assigned to the nodes:
        - CT-1001, index: 1
              
    3.3. Concentration Assignment:
        3.3.1 Check all "concentration" attributes in your input list and assign them to the right nodes:
        No concentration attributes are given in the input list.

    3.4. Ratio Assignment:
        3.4.1 Check all "ratio" attributes in your input list and assign them to the right nodes:
        The following ratios can be assigned to the nodes:
        - Pt: 50, index: 5
        - C: 30, index: 6
        - Pd: 20, index: 7

    3.5. Batch Number Assignment:
        3.5.1 Check all "batch number" attributes in your input list and assign them to the right nodes:
        No batch number attributes are given in the input list.
    
4. Create a list of dictionaries that contains the nodes and their attributes following the given format:

[{{"name": [["Catalyst", "inferred"]], "identifier": ["CT-1001", 1]}},
{{"name": [["Pt", 2]], "ratio": ["50", 5]}},
{{"name": [["C", 3]], "ratio": ["30", 6]}},
{{"name": [["Pd", 4]], "ratio": ["20", 7]}}]
"""},


                              ]


