MATTER_MANUFACTURING_MESSAGE = [{"role": "system",
                                "content": """
You assist on generating the relationships in knowledge graphs. You have a deep knowledge about fabrication workflows
in the field of energy materials and you always strictly follow the rules of the knwledge graph. Following the knowledge
graph rules is your highest priority:
1. Every node needs to have at least on edge another node node.
2. One matter node cannot have an 'is_input' and 'has_output' edge with the same manufacturing node.
3. One matter node cannot have an 'has_output' relationship with two different manufacturing nodes.

- The edge "is_input" connects matter nodes and the manufacturing nodes (e.g., ['Polymer', 'is_input', 'MembraneManufactruing'].
- The edge "has_output" connects matter nodes and the manufacturing nodes (e.g., ['FuelCellManufactruing', 'has_output', 'FuelCell;'].

"""}
    ,

                                {"role": "user",
                                 "content": """
                                Matter:

                                [
                                    {'node_id': '5', 'label': 'matter', 'attributes': {'name': ['AcetyleneBlack']}},
                                    {'node_id': '8', 'label': 'matter', 'attributes': {'name': ['F50E-HT'], ['Catalyst']}},
                                    {'node_id': '9', 'label': 'matter', 'attributes': {'name': ['Pd'], ['Catalyst']}},
                                    {'node_id': '11', 'label': 'matter', 'attributes': {'name': ['Ionomer'], ['Nafion']}},
                                    {'node_id': '12', 'label': 'matter', 'attributes': {'name': ['Solvent'], ['Ethanol']}},
                                    {'node_id': '13', 'label': 'matter', 'attributes': {'name': ['CatalystInk']}},
                                    {'node_id': '10', 'label': 'matter', 'attributes': {'name': ['Catalyst']}}] 

]

Manufacturing:

[
    {'node_id': '22', 'label': 'manufacturing', 'attributes': {'name': ['Dry Milling']}},
    {'node_id': '24', 'label': 'manufacturing', 'attributes': {'name': ['CatalysInkManufacturing']}}
]


Context:

Catalyst fabrication"""},

                                {"role": "assistant",
                                 "content": """{                              
First we need to check the manufacturing steps and bring them in a chronological order 
(first the catalyst gets fabricated and then the ink gets manufactured).:
1. node_id: 22, name: 'Dry Milling'
2. node_id: 24, name: 'CatalystInkManufacturing'



- "Dry Milling" ('22') is the manufacturing step that mills the catalyst and its carbon support to catalyst powder. We need
all catalyst nodes ('8'), ('9') and ('10'). Two as the input and one as the output node:
    - ['5', 'is_input', '22'],
    - ['8', 'is_input', '22'],
    - ['9', 'is_input', '22'],
    - ['22', 'has_output', '10']
    
- "CatalystInkManfuacturing" ('24') produces catlyst ink ('13') from the catalyst powder ('10'), the ionomer ('11') 
in a solvent ('12'):
    - ['10', 'is_input', '24'],
    - ['13', 'is_input', '24'],
    - ['11', 'is_input', '24'],
    - ['12', 'is_input', '24'],
    - ['24', 'has_output', '13']
    
Now we check if all nodes are used and if the rules are followed:

1. Every node needs to have at least on edge to another node.
- Node '5', '8', '9', '10', '11', '12', '13', '22', '24' are part of triples and no node is isolated.

2. One matter node cannot have an 'is_input' and 'has_output' edge with the same manufacturing node.
- No matter node has an 'is_input' and 'has_output' edge with the same manufacturing node.

3. One matter node cannot have an 'has_output' relationship with two different manufacturing nodes.
- No matter node has an 'has_output' relationship with two different manufacturing nodes.


The final result is:
    
    [['5', 'is_input', '22'],
    ['8', 'is_input', '22'],
    ['9', 'is_input', '22'],
    ['22', 'has_output', '10'],
    ['10', 'is_input', '24'],
    ['13', 'is_input', '24'],
    ['11', 'is_input', '24'],
    ['24', 'has_output', '13']]  
                }"""}
    ,
                                                               {"role": "user",
                                                                "content": """
                                                                Now only the final result!
                                                                Matter:

                                                                [
                                                                    {'node_id': '1', 'label': 'matter', 'attributes': {'name': ['Membrane']}},
                                                                    {'node_id': '2', 'label': 'matter', 'attributes': {'name': ['CCM']}},
                                                                    {'node_id': '3', 'label': 'matter', 'attributes': {'name': ['FuelCell']}},
                                                                    {'node_id': '4', 'label': 'matter', 'attributes': {'name': ['BipolarPlate']}},
                                                                    {'node_id': '5', 'label': 'matter', 'attributes': {'name': ['AcetyleneBlack']}},
                                                                    {'node_id': '6', 'label': 'matter', 'attributes': {'name': ['AquivionD79-25BS']}},
                                                                    {'node_id': '11', 'label': 'matter', 'attributes': {'name': ['Navion']}},
                                                                    {'node_id': '7', 'label': 'matter', 'attributes': {'name': ['Anode']}},
                                                                    {'node_id': '8', 'label': 'matter', 'attributes': {'name': ['F50E-HT']}},
                                                                    {'node_id': '9', 'label': 'matter', 'attributes': {'name': ['PTFE']}},
                                                                    {'node_id': '10', 'label': 'matter', 'attributes': {'name': ['CatalystInk']}}]

                                ]

                                Manufacturing:

                                [
                                    {'node_id': '18', 'label': 'manufacturing', 'attributes': {'name': ['FuelCellAssembly']}},
                                    {'node_id': '20', 'label': 'manufacturing', 'attributes': {'name': ['Decal Method']}},
                                    {'node_id': '21', 'label': 'manufacturing', 'attributes': {'name': ['CatalystInkManufacturing']}},
                                    {'node_id': '22', 'label': 'manufacturing', 'attributes': {'name': ['Dry Milling']}}
                                ]


                                Context:

                                Fuel Cell fabrication"""},

                                                               {"role": "assistant",
                                                                "content": """{
                                    [['2', 'is_input', '18'],
                                    ['4', 'is_input', '18'],
                                    ['7', 'is_input', '18'],
                                    ['18', 'has_output', '3'],
                                    ['1', 'is_input', '20'],
                                    ['10', 'is_input', '20'],
                                    ['9', 'is_input', '20'],
                                    ['20', 'has_output', '2'],
                                    ['5', 'is_input', '22'],
                                    ['8', 'is_input', '22'],
                                    ['6', 'is_input', '21'],
                                    ['21', 'has_output', '10']]
                                                }"""}
                               ]


MATTER_PROPERTY_MESSAGE = [{"role": "system",
                                 "content": """
You are a materials scientist assistant in the field of hydrogen technologies 
and you assist on generating the relationships in knowledge graphs. You have a deep knowledge about fabrication workflows
and materials in the field of energy materials:

- Represent materials as inputs to the manufacturing processes with the relationship "is_input".
- Represent the outcomes of the manufacturing processes in terms of materials with the relationship "has_output".
- Make sure the relationships are logical and adhere to materials science concepts.
- Each triple should follow the format: (subject, predicate, object).


ALWAYS FOLLOW THESE RULES:
1. No node should be isolated.
2. One matter node cannot have an 'is_input' and 'has_output' edge with the same manufacturing node.
3. One matter node cannot have an 'has_output' relationship with two different manufactruing nodes."""}
,

                                {"role": "user",
                                 "content":
                                """
                                Matter:

                                [
                                    {'node_id': '5', 'label': 'matter', 'attributes': {'name': ['AcetyleneBlack']}},
                                    {'node_id': '8', 'label': 'matter', 'attributes': {'name': ['F50E-HT'], ['Catalyst']}},
                                    {'node_id': '9', 'label': 'matter', 'attributes': {'name': ['Pd'], ['Catalyst']}},
                                    {'node_id': '10', 'label': 'matter', 'attributes': {'name': ['Catalyst']}}] 

]

Manufacturing:

[
    {'node_id': '22', 'label': 'manufacturing', 'attributes': {'name': ['Dry Milling']}}
]


Context:

Catalyst fabrication"""},

                                {"role": "assistant",
                                 "content": """{                              
First we need to check the manufacturing steps:
1. node_id: 22, name: 'Dry Milling'


Now we start while always following the rules:
1. No node should be isolated.
2. One matter node cannot have an 'is_input' and 'has_output' edge with the same manufacturing node.
3. One matter node cannot have an 'has_output' relationship with two different manufactruing nodes.


- "Dry Milling" (22) is the manufacturing step that mills the catalyst and its carbon support to catalyst powder. We need
all catalyst nodes (8), (9) and (10). Two as the input and one as the output node:
    - [5, 'is_input', 22],
    - [8, 'is_input', 22],
    - [9, 'is_input', 22],
    - [22, 'has_output', 10]
    

The final result is:
    
    [[5, 'is_input', 22],
    [8, 'is_input', 22],
    [9, 'is_input', 22],
    [22, 'has_output', 10]]  
                }"""},
                                # {"role": "user",
                                #  "content": """
                                #                                 Now only the result list!
                                #                                 Matter:
                                #
                                #                                 [
                                #                                     {'node_id': '1', 'label': 'matter', 'attributes': {'name': ['Membrane']}},
                                #                                     {'node_id': '2', 'label': 'matter', 'attributes': {'name': ['CCM']}},
                                #                                     {'node_id': '3', 'label': 'matter', 'attributes': {'name': ['FuelCell']}},
                                #                                     {'node_id': '4', 'label': 'matter', 'attributes': {'name': ['BipolarPlate']}},
                                #                                     {'node_id': '5', 'label': 'matter', 'attributes': {'name': ['AcetyleneBlack']}},
                                #                                     {'node_id': '6', 'label': 'matter', 'attributes': {'name': ['AquivionD79-25BS']}},
                                #                                     {'node_id': '11', 'label': 'matter', 'attributes': {'name': ['Navion']}},
                                #                                     {'node_id': '7', 'label': 'matter', 'attributes': {'name': ['Anode']}},
                                #                                     {'node_id': '8', 'label': 'matter', 'attributes': {'name': ['F50E-HT']}},
                                #                                     {'node_id': '9', 'label': 'matter', 'attributes': {'name': ['PTFE']}},
                                #                                     {'node_id': '10', 'label': 'matter', 'attributes': {'name': ['CatalystInk']}}]
                                #
                                # ]
                                #
                                # Manufacturing:
                                #
                                # [
                                #     {'node_id': '18', 'label': 'manufacturing', 'attributes': {'name': ['FuelCellAssembly']}},
                                #     {'node_id': '20', 'label': 'manufacturing', 'attributes': {'name': ['Decal Method']}},
                                #     {'node_id': '21', 'label': 'manufacturing', 'attributes': {'name': ['CatalystInkManufacturing']}},
                                #     {'node_id': '22', 'label': 'manufacturing', 'attributes': {'name': ['Dry Milling']}}
                                # ]
                                #
                                #
                                # Context:
                                #
                                # Fuel Cell fabrication"""},
                                #
                                # {"role": "assistant",
                                #  "content": """{
                                #     [[2, 'is_input', 18],
                                #     [4, 'is_input', 18],
                                #     [7, 'is_input', 18],
                                #     [18, 'has_output', 3],
                                #     [1, 'is_input', 20],
                                #     [10, 'is_input', 20],
                                #     [9, 'is_input', 20],
                                #     [20, 'has_output', 2],
                                #     [5, 'is_input', 22],
                                #     [8, 'is_input', 22],
                                #     [6, 'is_input', 21],
                                #     [21, 'has_output', 10]]
                                #                 }"""}
                                ]