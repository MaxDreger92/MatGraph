MATTER_MANUFACTURING_MESSAGE = [("system", """
You assist on generating the relationships in knowledge graphs. You have a deep knowledge about fabrication workflows
in the field of energy materials. Your only task is to generate relationships between matter and manufacturing nodes. 

Focus on connecting the nodes in a way that correctly represents the fabrication workflow the table is representing.
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

MATTER_PROPERTY_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You have a deep knowledge about fabrication workflows
and materials in the field of materials science. Your only task is to generate relationships between matter and property nodes.
You use the context and the deep knowledge in materials science to generate the relationships that correctly represent the information hidden in the table.
Rules you always follow:
1. Each property needs share exactly ONE 'has_property' edge with a matter node.
2. NEVER CONNECT one property with more than one manufacturing nodes.
"""),
("human",
 """Extract the relationships of the following nodes: {input} """),
("human", """Make sure to always follow the given format!"""),
("human",
"""Make sure that you followed the rule-set:
1. Each property needs share exactly ONE 'has_property' edge with a matter node.
2. NEVER CONNECT one property with more than one manufacturing nodes.
""")
                           ]

HAS_PARAMETER_MESSAGE = [("system",
"""You are a world class knowledge-graph generating algorithm. You have a deep knowledge about fabrication workflows
and materials in the field of materials science. Your only task is to generate relationships between manufacturing and parameter nodes.
You use the context and the deep knowledge in materials science to generate the relationships that correctly represent the information hidden in the table.
Rules you always follow:
1. Each parameter needs share exactly ONE 'has_parameter' edge with a manufacturing, or measurement node.
2. NEVER CONNECT one parameter with more than one manufacturing/measurement nodes.
"""),
("human", """Extract the relationships of the following nodes: {input} """),
("human", """Make sure to always follow the given format!"""),
("human",
"""Make sure that you followed the rule-set:
1. Each parameter needs share exactly ONE 'has_parameter' edge with a manufacturing, or measurement node.
2. NEVER CONNECT one parameter with more than one manufacturing/measurement nodes.
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

