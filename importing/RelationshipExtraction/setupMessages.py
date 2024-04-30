MATTER_MANUFACTURING_MESSAGE = [("system", """
You assist on generating the relationships in knowledge graphs. You have a deep knowledge about fabrication workflows
in the field of energy materials. Your only task is to generate relationships between matter and manufacturing nodes. 
HINTS:
- Connect the nodes that they form a sequence that correctly represents the fabrication workflow.
""")
,
("human", """Extract the relationships of the following nodes: {input} """),
("human", """Make sure to always follow the given format!"""),
("human",
"""Make sure that you followed the rule-set:
1. Every node needs to have at least one edge another node.
2. Matter nodes cannot have an 'is_manufacturing_input' and 'has_manufacturing_output' edge with the same Manufacturing node.
3. Matter nodes cannot have an 'is_manufacturing_output' relationship with two different Manufacturing nodes.
4. The triples you generate have to consist of node_id, relationship, node_id. The node_ids need to belong to existing nodes.
""")
]

HAS_PARAMETER_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You have a deep knowledge about fabrication workflows
and materials in the field of materials science. Your only task is to assign each Parameter node to the correct Manufacturing/Measurement node.
As additional you are given the Scientific context and the table data the nodes were extracted from.
The input data has the following structure:
- Scientific context
-Table header
-First row of the table
-List of manufacturing or measurement nodes
-List of parameter nodes

Each node has:
- id
- attributes
- value (attribute value)
- index (column index from which the attribute was extracted)


Rules you always follow:
1. Each parameter needs share exactly ONE 'has_parameter' edge with a manufacturing, or measurement node.
2. When you are unsure connect the nodes that are in close proximity in the table (consider the "index" keys of the attributes and the table).
3. The source node is always the manufacturing or measurement node.
4. The target node is always the parameter node.
"""),
("human", """Extract all "has_parameter" relationships from the data: {input} """),
("human",
"""Make sure to always follow the given format and that you create relationships that form correct triples!"""),
("human",
"""Make sure that you followed the rule-set:
1. Each parameter needs share exactly ONE 'has_parameter' edge with a manufacturing, or measurement node.
2. When you are unsure connect the nodes that are in close proximity in the table (consider the "index" keys of the attributes table).
3. The source node is always the manufacturing or measurement node.
4. The target node is always the parameter node.
""")]

MATTER_MATTER_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You have a deep knowledge about fabrication workflows
and materials in the field of materials science. Your only task is to assign Matter nodes to their components.
As additional you are given the Scientific context and the table data the nodes were extracted from.
The input data has the following structure:
- Scientific context
-Table header
-First row of the table
-List of matter nodes

Each node has:
- id
- attributes
- value (attribute value)
- index (column index from which the attribute was extracted)


Rules you always follow:
1. Connect matter nodes to their parts/components by the 'has_part' relationship.
2. The source node is always the whole while the target node is its part/component.
"""),
("human", """Extract all "has_part" relationships from the data: {input} """),
("human",
"""Make sure to always follow the given format and that you create relationships that form correct triples!"""),
("human",
"""Make sure that you followed the rule-set:
1. Connect matter nodes to their parts/components by the 'has_part' relationship.
2. The source node is always the whole while the target node is its part/component.
""")]

MANUFACTURING_MANUFACTURING_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You have a deep knowledge about fabrication workflows
and materials in the field of materials science. Your only task is to assign manufacturing nodes to their subprocesses.
As additional you are given the Scientific context and the table data the nodes were extracted from.
You do only generate relationsghips from the process to it subprocess. 
you do not create relationships from proces steps to the following proces steps.
The input data has the following structure:
- Scientific context
-Table header
-First row of the table
-List of manufacturing nodes

Each node has:
- id
- attributes
- value (attribute value)
- index (column index from which the attribute was extracted)


Rules you always follow:
1. Connect manufacturing nodes to their parts/subprocesses by the 'has_part' relationship.
2. The source node is always the whole while the target node is its part/subprocess.
"""),
("human", """Extract all "has_part" relationships from the data: {input} """),
("human",
"""Make sure to always follow the given format and that you create relationships that form correct triples!"""),
("human",
"""Make sure that you followed the rule-set:
1. Connect manufacturing nodes to their parts/subrpocess by the 'has_part' relationship.
2. The source node is always the whole while the target node is its part/subprocess.
""")]

MEASUREMENT_MEASUREMENT_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You have a deep knowledge about fabrication workflows
and materials in the field of materials science. Your only task is to assign measurement nodes to their subprocesses.
As additional you are given the Scientific context and the table data the nodes were extracted from.
The input data has the following structure:
- Scientific context
-Table header
-First row of the table
-List of measurement nodes

Each node has:
- id
- attributes
- value (attribute value)
- index (column index from which the attribute was extracted)


Rules you always follow:
1. Connect measurement nodes to their parts/subprocesses by the 'has_part' relationship.
2. The source node is always the whole while the target node is its part/subprocess.
"""),
("human", """Extract all "has_part" relationships from the data: {input} """),
("human",
"""Make sure to always follow the given format and that you create relationships that form correct triples!"""),
("human",
"""Make sure that you followed the rule-set:
1. Connect measurement nodes to their parts/subprocess by the 'has_part' relationship.
2. The source node is always the whole while the target node is its part/component.
""")]

MATTER_PROPERTY_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You have a deep knowledge about fabrication workflows
and materials in the field of materials science. Your only task is to assign each Property node to the correct Matter node.
As additional you are given the Scientific context and the table data the nodes were extracted from.
The input data has the following structure:
- Scientific context
-Table header
-First row of the table
-List of matter nodes
-List of property nodes

Each node has:
- id
- attributes
- value (attribute value)
- index (column index from which the attribute was extracted)


Rules you always follow:
1. Each property node needs share exactly ONE 'has_property' edge with a matter node.
2. Each property node needs to be connected with a matter node that fits the property (e.g., a battery capacity should be connected to a battery).
3. When you are unsure connect the nodes that are in close proximity in the table (consider the "index" keys of the attributes and the table).
4. The source node is always the matter node.
5. The target node is always the property node.
"""),
("human", """Extract all "has_property" relationships from the data: {input} """),
("human",
"""Make sure to always follow the given format and that you create relationships that form correct triples!"""),
("human",
"""Make sure that you followed the rule-set:
1. Each property node needs share exactly ONE 'has_property' edge with a matter node.
2. Each property node needs to be connected with a matter node that fits the property (e.g., a battery capacity should be connected to a battery).
3. When you are unsure connect the nodes that are in close proximity in the table (consider the "index" keys of the attributes and the table).
4. The source node is always the matter node.
5. The target node is always the property node.
""")
]

PROPERTY_MEASUREMENT_MESSAGE = [("system", """
You are a world class knowledge-graph generating algorithm. You have a deep knowledge about fabrication workflows
and materials in the field of materials science. Your only task is to generate relationships between property and measurement nodes.
You use the context and the deep knowledge in materials science to generate the relationships that correctly represent the information hidden in the table.
Rules you always follow:
1. Every measurement node needs to have at least on edge another property node.
2. Each property node can only share a 'has_measurement_output' with one measurement node.
"""),
("human", """Extract the relationships of the following nodes: {input} """),
("human", """Make sure to always follow the given format!"""),
("human",
"""Make sure that you followed the rule-set:
1. Every measurement node needs to have at least on edge another property node.
2. Each property node can only share a 'has_measurement_output' with one measurement node.""")
]

HAS_PARAMETER_CORRECTION_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You excell in correcting relationships between matter and property nodes.
Your task is to correct a given set of triples that represent the relationships between matter and property nodes.
You will recieve:
- context
- list of matter nodes
- list of property nodes
- list of triples
- instructions on how to correct the triples"""),
("human", """Correct the following '{rel_type}' relationships: {graph}
They were extracted from the following lists of nodes
{label_one}: {node_list_one}
{label_two}: {node_list_two}
They have the following inconsistencies with the data model:
{inconsistencies}
Please correct them and return a corrected list of '{rel_type}' relationships!"""),
("human", """Make sure to always follow the given format!"""),
]

HAS_PROPERTY_CORRECTION_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You excell in correcting relationships between matter and property nodes.
Your task is to correct a given set of triples that represent the relationships between matter and property nodes.
You will recieve:
- context
- list of matter nodes
- list of property nodes
- list of triples
- instructions on how to correct the triples"""),
("human", """Correct the following '{rel_type}' relationships: {graph}
They were extracted from the following lists of nodes
{label_one}: {node_list_one}
{label_two}: {node_list_two}
They have the following inconsistencies with the data model:
{inconsistencies}
Please correct them and return a corrected list of '{rel_type}' relationships!"""),
("human", """Make sure to always follow the given format!"""),
]

PROPERTY_MEASUREMENT_CORRECTION_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You excell in correcting relationships between matter and property nodes.
Your task is to correct a given set of triples that represent the relationships between matter and property nodes.
You will recieve:
- context
- list of matter nodes
- list of property nodes
- list of triples
- instructions on how to correct the triples"""),
("human", """Correct the following '{rel_type}' relationships: {graph}
They were extracted from the following lists of nodes
{label_one}: {node_list_one}
{label_two}: {node_list_two}
They have the following inconsistencies with the data model:
{inconsistencies}
Please correct them and return a corrected list of '{rel_type}' relationships!"""),
("human", """Make sure to always follow the given format!"""),
]

MATTER_MANUFACTURING_CORRECTION_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You excell in correcting relationships between matter and property nodes.
Your task is to correct a given set of triples that represent the relationships between matter and property nodes.
You will recieve:
- context
- list of matter nodes
- list of property nodes
- list of triples
- instructions on how to correct the triples"""),
("human", """Correct the following '{rel_type}' graph: {graph}
They were extracted from the following lists of nodes
{label_one}: {node_list_one}
{label_two}: {node_list_two}
They have the following inconsistencies with the data model:
{inconsistencies}
Please correct them and return a corrected list of '{rel_type}' relationships!"""),
("human", """Make sure to always follow the given format!"""),
]

MATTER_MATTER_CORRECTION_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You excell in correcting 'has_part' relationships between matter nodes.
You will recieve:
- context
- list of matter nodes
-list of triples
- instructions on how to correct the triples"""),
("human", """Correct the following '{rel_type}' graph: {graph}
They were extracted from the following list of nodes
{label_one}: {node_list_one}
They have the following inconsistencies with the data model:
{inconsistencies}
Please correct them and return a corrected list of '{rel_type}' relationships!"""),
("human", """Make sure to always follow the given format!"""),
]

MANUFACTURING_MANUFACTURING_CORRECTION_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You excell in correcting 'has_part' relationships between manufacturing nodes.
You will recieve:
- context
- list of manufacturing nodes
-list of triples
- instructions on how to correct the triples"""),
("human", """Correct the following '{rel_type}' graph: {graph}
They were extracted from the following list of nodes
{label_one}: {node_list_one}
They have the following inconsistencies with the data model:
{inconsistencies}
Please correct them and return a corrected list of '{rel_type}' relationships!"""),
("human", """Make sure to always follow the given format!"""),
]

MEASUREMENT_MEASUREMENT_CORRECTION_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You excell in correcting 'has_part' relationships between measurement nodes.
You will recieve:
- context
- list of measurement nodes
-list of triples
- instructions on how to correct the triples"""),
("human", """Correct the following '{rel_type}' graph: {graph}
They were extracted from the following list of nodes
{label_one}: {node_list_one}
They have the following inconsistencies with the data model:
{inconsistencies}
Please correct them and return a corrected list of '{rel_type}' relationships!"""),
("human", """Make sure to always follow the given format!"""),
]