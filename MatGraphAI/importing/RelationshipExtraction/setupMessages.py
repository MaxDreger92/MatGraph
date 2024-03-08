MATTER_MANUFACTURING_MESSAGE = [{"role": "system",
                                "content": """
You assist on generating the relationships in knowledge graphs. You have a deep knowledge about fabrication workflows
in the field of energy materials and you always strictly follow the rules of the knowledge graph. Following the knowledge
graph rules is your highest priority:
1. Every node needs to have at least one edge another node node.
2. Matter nodes cannot have an 'is_manufacturing_input' and 'is_manufacturing_output' edge with the same manufacturing node.
3. Matter node cannot have an 'is_manufacturing_output' relationship with two different manufacturing nodes.
4. Matter nodes mau never be connected to other matter nodes.

- The edge "is_manufacturing_input" connects matter nodes and the manufacturing nodes (e.g., ['Polymer', 'is_manufacturing_input', 'MembraneManufacturing'].
- The edge "is_manufacturing_output" connects matter nodes and the manufacturing nodes (e.g., ['FuelCellManufacturing', 'is_manufacturing_output', 'FuelCell;'].


YOU USE YOUR EXTENSIVE KNOWLEDGE TO CREATE FABRICATION WORKFLOWS THAT REPRESENT THE  FABRICATION OF THE GIVEN DEVICES IN THE BEST WAY POSSIBLE.

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



- "Dry Milling" ('22') is the manufacturing step that mills the catalyst and its carbon support to catalyst powder. The 
process requires catalysts (('8'), ('9') and ('10')). Two as the input and one as the output node:
    - ['5', 'is_manufacturing_input', '22'],
    - ['8', 'is_manufacturing_input', '22'],
    - ['9', 'is_manufacturing_input', '22'],
    - ['22', 'is_manufacturing_output', '10']
    
- "CatalystInkManufacturing" ('24') produces catlyst ink ('13') from the catalyst powder ('10'), the ionomer ('11') 
in a solvent ('12'):
    - ['10', 'is_manufacturing_input', '24'],
    - ['13', 'is_manufacturing_input', '24'],
    - ['11', 'is_manufacturing_input', '24'],
    - ['12', 'is_manufacturing_input', '24'],
    - ['24', 'is_manufacturing_output', '13']
    
Now we check if all nodes are used and if the rules are followed:

1. Every node needs to have at least on edge to another node.
- Node '5', '8', '9', '10', '11', '12', '13', '22', '24' are part of triples and no node is isolated.

2. One matter node cannot have an 'is_manufacturing_input' and 'is_manufacturing_output' edge with the same manufacturing node.
- No matter node has an 'is_manufacturing_input' and 'is_manufacturing_output' edge with the same manufacturing node.

3. One matter node cannot have an 'is_manufacturing_output' relationship with two different manufacturing nodes.
- No matter node has an 'is_manufacturing_output' relationship with two different manufacturing nodes.


The final result is:
    
    [['5', 'is_manufacturing_input', '22'],
    ['8', 'is_manufacturing_input', '22'],
    ['9', 'is_manufacturing_input', '22'],
    ['22', 'is_manufacturing_output', '10'],
    ['10', 'is_manufacturing_input', '24'],
    ['13', 'is_manufacturing_input', '24'],
    ['11', 'is_manufacturing_input', '24'],
    ['24', 'is_manufacturing_output', '13']]  
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
                                    [['2', 'is_manufacturing_input', '18'],
                                    ['4', 'is_manufacturing_input', '18'],
                                    ['7', 'is_manufacturing_input', '18'],
                                    ['18', 'is_manufacturing_output', '3'],
                                    ['1', 'is_manufacturing_input', '20'],
                                    ['10', 'is_manufacturing_input', '20'],
                                    ['9', 'is_manufacturing_input', '20'],
                                    ['20', 'is_manufacturing_output', '2'],
                                    ['5', 'is_manufacturing_input', '22'],
                                    ['8', 'is_manufacturing_input', '22'],
                                    ['6', 'is_manufacturing_input', '21'],
                                    ['21', 'is_manufacturing_output', '10']]
                                                }"""}
                               ]


MATTER_PROPERTY_MESSAGE = [{"role": "system",
                                 "content": """
You are a materials scientist assistant in the field of hydrogen technologies 
and you assist on generating the relationships in knowledge graphs. You have a deep knowledge about fabrication workflows
and materials in the field of energy materials:

- Pair matter nodes with properties with "has_property" edges.
- Make sure the relationships are logical and adhere to materials science concepts.
- Each triple should follow the format: (subject, predicate, object).


ALWAYS FOLLOW THIS RULE:

Each property needs share exactly ONE 'has_property' edge with a matter node.
NEVER CONNECT one property with more than one manufacturing nodes.
If a property could fit to more than one matter node assign it to the one that its id is closest to!


"""}
,

                                {"role": "user",
                                 "content":
                                """
                                
                                Matter:

                                [
                                    {'node_id': '5', 'label': 'matter', 'attributes': {'name': ['AcetyleneBlack']}},
                                    {'node_id': '6', 'label': 'matter', 'attributes': {'name': ['F50E-HT'], ['Catalyst']}},
                                    {'node_id': '9', 'label': 'matter', 'attributes': {'name': ['Pd'], ['Catalyst']}},
                                    {'node_id': '10', 'label': 'matter', 'attributes': {'name': ['AquivionD79-25BS']}},
                                    {'node_id': '8', 'label': 'matter', 'attributes': {'name': ['CatalystLayer']}}
                                ]

                                Property:

                                [
                                    {'node_id': '22', 'label': 'property', 'attributes': {'name': ['EW'], 'value': '790'}},
                                    {'node_id': '24', 'label': 'property', 'attributes': {'name': ['I/C'], 'value': '0.9'}},
                                    {'node_id': '26', 'label': 'property', 'attributes': {'name': ['SEM CCL thickness (µm)'], 'value': '790', 'unit': 'µm'}},
                                    {'node_id': '29', 'label': 'property', 'attributes': {'name': ['Pt loading (mg/cm2geo)'], 'value': '0.25'}}
                                ]
Context:

Catalyst fabrication"""},

                                {"role": "assistant",
                                 "content": """{
We need to make sure that each property is assigned to exactly one matter node. 
Therefore we go through all property nodes and assign them to a matter node.


- "EW" (22) is the abbreviation for equivalent weight and is a property of polymers and ionomers. The ionomer 
AquivionD79-25BS (10) has this property and the D79 in its name is referencing the equivalent weight.
Therefore we assign the property node 22 to the matter node 10.
    - ['10', 'has_property', '22']

- "I/C" (24) is the abbreviation for ionomer to carbon ratio and is a property of catalyst layers. The catalyst layer
(8) has this property. Therefore we assign the property node 24 to the matter node 8.
    - ['8', 'has_property', '24']

- "SEM CCL thickness (µm)" (26) is the abbreaviation for scanning electron microscopy catalyst layer thickness and is a 
property of catalyst layers. The catalyst layer (8) has this property. Therefore we assign the property node 26 to the
matter node 8.
    - ['8', 'has_property', '26']
    
- "PtLoading" (29) is the abbreaviation for platinum loading and is a property of catalyst layers. The catalystlayer (8) has this
property as the unit of the property is mass per area. Therefore we assign the property node 29 to the matter node 8.
    - ['8', 'has_property', '29']
    
The final result is:

    [['10', 'has_property', '22'],
    ['8', 'has_property', '24'],
    ['8', 'has_property', '26'],
    ['8', 'has_property', '29']]
                }"""},
                                {"role": "user",
                                 "content": """
                                            Now only the result list!


                               
                                Matter:

                                [
                                {'node_id': '5', 'label': 'matter', 'attributes': {'name': ['Electrolyzer']}},
                                {'node_id': '6', 'label': 'matter', 'attributes': {'name': ['NiCu'], ['Catalyst']}},

                                ]
                                
                                Properties:

                                [
                                    {'node_id': '18', 'label': 'property', 'attributes': {'name': ['Performance']}},
                                    {'node_id': '20', 'label': 'property', 'attributes': {'name': ['XPS peak']}},
                                    {'node_id': '21', 'label': 'property', 'attributes': {'name': ['Overpotential']}}
                                ]


                                Context:

                                Electrolyzers"""},

                                {"role": "assistant",
                                 "content": """{
                                    [['5', 'has_property', '18'],
                                    ['6', 'has_property', '20'],
                                    ['6', 'has_property', '21']]
                                                }"""}
                                ]

MANUFACTURING_PARAMETER_MESSAGE = [{"role": "system",
                            "content": """
You are a materials scientist assistant in the field of hydrogen technologies 
and you assist on generating the relationships in knowledge graphs. You have a deep knowledge about fabrication workflows
and materials in the field of energy materials:

- Pair manufacturing and measurement nodes with parameter nodes with "has_parameter" edges.
- Make sure the relationships are logical and the parameters fit the manufacturing steps you assign them to.
- Each triple should follow the format: (subject, predicate, object).


ALWAYS FOLLOW THIS RULE:

1. Each parameter needs share exactly ONE 'has_parameter' edge with a matter node.
2. NEVER CONNECT one parameter with more than one manufacturing/measurement nodes.
3. There are no duplicates among the nodes as long as they differ in their node_id.
4. If there are combinations that both are possible and have exactly the same probability, choose them according to their 
index in the list. 

"""},
                           {"role": "user",
                            "content":
                                """
                                
                                Manufacturing, Measurement:

                                [
                                    {'node_id': '5', 'label': 'manufacturing', 'attributes': {'name': ['hot pressing']}},
                                    {'node_id': '6', 'label': 'manufacturing', 'attributes': {'name': ['dry milling']}},
                                    {'node_id': '9', 'label': 'measurement', 'attributes': {'name': ['CL DVS sorption at 95%RH (% mass change/cm2geo)']}},
                                    {'node_id': '10', 'label': 'measurement', 'attributes': {'name': ['CL DVS sorption at 80%RH (% mass change/cm2geo)']}}
                                ]
                                
                                Parameter:

                                [
                                    {'node_id': '22', 'label': 'parameter', 'attributes': {'name': ['RH'], 'value': '95'}},
                                    {'node_id': '24', 'label': 'parameter', 'attributes': {'name': ['RH'], 'value': '80'}},
                                    {'node_id': '26', 'label': 'parameter', 'attributes': {'name': ['Temperature'], 'value': '150', 'unit': 'C'}},
                                    {'node_id': '27', 'label': 'parameter', 'attributes': {'name': ['Hot_Pressing_Time'], 'value': '120'}},
                                    {'node_id': '29', 'label': 'parameter', 'attributes': {'name': ['DryMillingTime'], 'value': '120'}},                                   
                                ]
                                

Context:

Catalyst fabrication"""},

                           {"role": "assistant",
                            "content": """{
We need to make sure that each parameter is assigned to exactly one matter node. 
Therefore we go through all property nodes and assign them to a matter node.


- "RH" (22) with value 95 is the abbreviation for relative humidity and is a parameter of 'CL DVS sorption at 
'95%RH (% mass change/cm2geo)' (9), because  The name contains '95%RH'. 
Therefore we assign the parameter node 22 to the matter node 9.
    - ['10', 'has_parameter', '22']

- "RH" (24) with value 80 is the abbreviation for relative humidity and is a parameter of 'CL DVS sorption at
'80%RH (% mass change/cm2geo)' (10), because  The name contains '80%RH'.
Therefore we assign the parameter node 24 to the matter node 10.
    - ['8', 'has_parameter', '24']

- "Temperature" (26) with value 150 is a parameter of 'hot pressing' (5), because as its a manufacturing step for 
which the temperature is very important. Therefore we assign the parameter node 26 to the matter node 5.
    - ['5', 'has_parameter', '26']
    
- "Hot_Pressing_Time" (27) with value 120 is a parameter of 'hot pressing' (5), because as its name contains 'hot pressing'.
Therefore we assign the parameter node 27 to the matter node 5.
    - ['5', 'has_parameter', '27']

- "DryMillingTime" (29) with value 120 is a parameter of 'dry milling' (6), because as its name contains 'dry milling'.
Therefore we assign the parameter node 29 to the matter node 6.
    - ['6', 'has_parameter', '29']
    
The final result is:

    [['10', 'has_parameter', '22'],
    ['8', 'has_parameter', '24'],
    ['8', 'has_parameter', '26'],
    ['8', 'has_parameter', '27'],
    ['8', 'has_parameter', '29']]
    
                }"""},
                           {"role": "user",
                            "content": """
                                            Now only the result list!



                                Manufacturing/Measurement:

                                [
                                {'node_id': '5', 'label': 'manufacturing', 'attributes': {'name': ['Heating']}},
                                {'node_id': '6', 'label': 'manufacturing', 'attributes': {'name': ['Drying']}},

                                ]

                                Parameter:

                                [
                                    {'node_id': '18', 'label': 'parameter', 'attributes': {'name': ['Heating rate']}},
                                    {'node_id': '20', 'label': 'parameter', 'attributes': {'name': ['Heating Time']}},
                                    {'node_id': '21', 'label': 'parameter', 'attributes': {'name': ['Drying Time']}}
                                ]


                                Context:

                                Electrolyzers"""},

                           {"role": "assistant",
                            "content": """{
                                    [['5', 'has_parameter', '18'],
                                    ['5', 'has_parameter', '20'],
                                    ['6', 'has_parameter', '21']]
                                                }"""}
                           ]

PROPERTY_MEASUREMENT_MESSAGE = [{"role": "system",
                                 "content": """
You assist on generating the relationships in knowledge graphs. You have a deep knowledge about fabrication workflows
in the field of energy materials and you always strictly follow the rules of the knowledge graph. Following the knowledge
graph rules is your highest priority:
1. Every measurement node needs to have at least on edge another property node.
2. Each property node can only share a 'has_measurement_output' with one measurement node.

- The edge "has_measurement_output" connects measurement nodes and property nodes 
(e.g., ['SEMMeasurement', 'has_measurement_output', 'Particle Size Distribution'].

"""}
    ,

                                {"role": "user",
                                 "content": """
                                Measurement:

                                [
                                    {'node_id': '5', 'label': 'measurement', 'attributes': {'name': ['SEM Measurement']}},
                                    {'node_id': '8', 'label': 'measurement', 'attributes': {'name': ['XRD']}},
                                    {'node_id': '9', 'label': 'measurement', 'attributes': {'name': ['maximum power output']}}] 

]

Property:

[
    {'node_id': '22', 'label': 'property', 'attributes': {'name': ['Particle Size Distribution']}},
    {'node_id': '23', 'label': 'property', 'attributes': {'name': ['Performance']}},
    {'node_id': '25', 'label': 'property', 'attributes': {'name': ['Layer Thickness']}},
    {'node_id': '26', 'label': 'property', 'attributes': {'name': ['Porosity']}},
    {'node_id': '28', 'label': 'property', 'attributes': {'name': ['PlatinumLoading']}},
    {'node_id': '30', 'label': 'property', 'attributes': {'name': ['Dislocation Density']}},    
    {'node_id': '31', 'label': 'property', 'attributes': {'name': ['Crystallinity']}}
]


Context:

Catalyst fabrication"""},

                                {"role": "assistant",
                                 "content": """{                              
Since every measurement requires to be connected to at least one property node, we need to connect the measurement
first.
1. node_id: 5, name: 'SEM Measurement'
2. node_id: 8, name: 'XRD'
3. node_id: 9, name: 'maximum power output'



- "SEM Measurement" (5) is a measurement of 'Particle Size Distribution' (22), Layer Thickness (25), Porosity (26) and
PlatinumLoading (28).
Therefore we assign the measurement node 5 to the property node 22.
    - ['5', 'has_measurement_output', '22']
    - ['5', 'has_measurement_output', '25']
    - ['5', 'has_measurement_output', '26']
    - ['5', 'has_measurement_output', '28']

- "XRD" (8) is a measurement of 'Crystallinity' (31) and 'Dislocation Density' (30).
Therefore we assign the measurement node 8 to the property node 31.
    - ['8', 'has_measurement_output', '31']
    - ['8', 'has_measurement_output', '30']

- "maximum power output" (9) is a measurement of 'Performance' (23).
Therefore we assign the measurement node 9 to the property node 23.
    - ['9', 'has_measurement_output', '23']


The final result is:
    
    [['5', 'has_measurement_output', '22'],
    ['5', 'has_measurement_output', '25'],
    ['5', 'has_measurement_output', '26'],
    ['5', 'has_measurement_output', '28'],
    ['8', 'has_measurement_output', '31'],
    ['8', 'has_measurement_output', '30'],
    ['9', 'has_measurement_output', '23']]
                }"""}
    ,
    {"role": "user",
     "content": """
        Now only the final result!
        Measurement:
    
        [
            {'node_id': '1', 'label': 'measurement', 'attributes': {'name': ['efficiency measurement']}},
            {'node_id': '2', 'label': 'measurement', 'attributes': {'name': ['cycling']}},
    
    ]

                                Manufacturing:

                                [
                                    {'node_id': '18', 'label': 'property', 'attributes': {'name': ['performance']}},
                                    {'node_id': '20', 'label': 'property', 'attributes': {'name': ['cycle life']}}
                                ]


                                Context:

                                Battery fabrication"""},

                                {"role": "assistant",
                                 "content": """{
                                    [['1', 'has_measurement_output', '18'],
                                    ['2', 'has_measurement_output', '20']]
                                                }"""}
                                ]