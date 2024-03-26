MATTER_MANUFACTURING_EXAMPLES = [
    {
        'input': {
            """    
Context: FuelCell Fabrication                            
matter: [
    {'node_id': '5', 'label': 'matter', 'attributes': {'name': ['AcetyleneBlack']}},
    {'node_id': '8', 'label': 'matter', 'attributes': {'name': ['F50E-HT'], ['Catalyst']}},
    {'node_id': '9', 'label': 'matter', 'attributes': {'name': ['Pd'], ['Catalyst']}},
    {'node_id': '11', 'label': 'matter', 'attributes': {'name': ['Ionomer'], ['Nafion']}},
    {'node_id': '12', 'label': 'matter', 'attributes': {'name': ['Solvent'], ['Ethanol']}},
    {'node_id': '13', 'label': 'matter', 'attributes': {'name': ['CatalystInk']}},
    {'node_id': '10', 'label': 'matter', 'attributes': {'name': ['Catalyst']}}] 
]

manufacturing: [
    {'node_id': '22', 'label': 'manufacturing', 'attributes': {'name': ['Dry Milling']}},
    {'node_id': '24', 'label': 'manufacturing', 'attributes': {'name': ['CatalysInkManufacturing']}}
]"""
        },
        'output': """{
  "output": [
    {
      "rel_type": "is_manufacturing_input",
      "connection": ["5", "22"]
    },
    {
      "rel_type": "is_manufacturing_input",
      "connection": ["8", "22"]
    },
    {
      "rel_type": "is_manufacturing_input",
      "connection": ["9", "22"]
    },
    {
      "rel_type": "has_manufacturing_output",
      "connection": ["22", "10"]
    },
    {
      "rel_type": "is_manufacturing_input",
      "connection": ["10", "24"]
    },
    {
      "rel_type": "is_manufacturing_input",
      "connection": ["13", "24"]
    },
    {
      "rel_type": "is_manufacturing_input",
      "connection": ["11", "24"]
    },
    {
      "rel_type": "has_manufacturing_output",
      "connection": ["24", "13"]
    }
  ]
}"""
    },
]

MATTER_PROPERTY_EXAMPLES = [
    {
        'input': """
Context: FuelCell Fabrication
matter: [
    {'node_id': '5', 'label': 'matter', 'attributes': {'name': ['AcetyleneBlack']}},
    {'node_id': '6', 'label': 'matter', 'attributes': {'name': ['F50E-HT'], ['Catalyst']}},
    {'node_id': '9', 'label': 'matter', 'attributes': {'name': ['Pd'], ['Catalyst']}},
    {'node_id': '10', 'label': 'matter', 'attributes': {'name': ['AquivionD79-25BS']}},
    {'node_id': '8', 'label': 'matter', 'attributes': {'name': ['CatalystLayer']}}
property: [
    {'node_id': '22', 'label': 'property', 'attributes': {'name': ['EW'], 'value': '790'}},
    {'node_id': '24', 'label': 'property', 'attributes': {'name': ['I/C'], 'value': '0.9'}},
    {'node_id': '26', 'label': 'property', 'attributes': {'name': ['SEM CCL thickness (µm)'], 'value': '790', 'unit': 'µm'}},
    {'node_id': '29', 'label': 'property', 'attributes': {'name': ['Pt loading (mg/cm2geo)'], 'value': '0.25'}}
]""",
        'output': """{"output": [
    {
      "rel_type": "has_property",
      "connection": ["10", "22"]
    },
    {
      "rel_type": "has_property",
      "connection": ["8", "24"]
    },
    {
      "rel_type": "has_property",
      "connection": ["8", "26"]
    },
    {
      "rel_type": "has_property",
      "connection": ["8", "29"]
    }
  ] """}

]

HAS_PARAMETER_EXAMPLES = [
    {
        'input': """
Context: FuelCell Fabrication
manufacturing/measurement: [
                                    {'node_id': '5', 'label': 'manufacturing', 'attributes': {'name': ['hot pressing']}},
                                    {'node_id': '6', 'label': 'manufacturing', 'attributes': {'name': ['dry milling']}},
                                    {'node_id': '9', 'label': 'measurement', 'attributes': {'name': ['CL DVS sorption at 95%RH (% mass change/cm2geo)']}},
                                    {'node_id': '10', 'label': 'measurement', 'attributes': {'name': ['CL DVS sorption at 80%RH (% mass change/cm2geo)']}}
                                ]
parameter: [
                                    {'node_id': '22', 'label': 'parameter', 'attributes': {'name': ['RH'], 'value': '95'}},
                                    {'node_id': '24', 'label': 'parameter', 'attributes': {'name': ['RH'], 'value': '80'}},
                                    {'node_id': '26', 'label': 'parameter', 'attributes': {'name': ['Temperature'], 'value': '150', 'unit': 'C'}},
                                    {'node_id': '27', 'label': 'parameter', 'attributes': {'name': ['Hot_Pressing_Time'], 'value': '120'}},
                                    {'node_id': '29', 'label': 'parameter', 'attributes': {'name': ['DryMillingTime'], 'value': '120'}},                                   
                                ]""",
        'output': """{
  "output": [
    {
      "rel_type": "has_parameter",
      "connection": ["10", "22"]
    },
    {
      "rel_type": "has_parameter",
      "connection": ["8", "24"]
    },
    {
      "rel_type": "has_parameter",
      "connection": ["8", "26"]
    },
    {
      "rel_type": "has_parameter",
      "connection": ["8", "27"]
    },
    {
      "rel_type": "has_parameter",
      "connection": ["8", "29"]
    }
  ]
}"""
    }]


