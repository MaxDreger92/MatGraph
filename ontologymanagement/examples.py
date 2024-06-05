MATTER_ONTOLOGY_ASSISTANT_EXAMPLES = \
    [{"input": """NickelBasedDiamondLikeCarbonCoatedBipolarPlate""",
      "output": """{"output": {
"name": "Nickel-Based Diamond-Like Carbon Coated Bipolar Plate",
"alternative_labels": ["Ni-DLC Coated Bipolar Plate", 
"Nickel-DLC Coated Bipolar Plate", 
"Ni-DLC BPP", 
]
}
}"""},
     {"input": """NRE211""",
      "output": """{"output": {
"name": "NRE211",
"alternative_labels": ["LiNi0.8Mn0.1Co0.1O2", 
"Nickel-Rich Layered Oxide Cathode", 
]
}}"""},
     {"input": """MembraneElectrodeAssembly""",
      "output": """{"output": {
"name": "Membrane Electrode Assembly",
"alternative_labels": [
MEA", 
"Proton Exchange Membrane Assembly", 
"PEM Assembly"]
}
}"""}]
QUANTITY_ONTOLOGY_ASSISTANT_EXAMPLES = \
    [{"input": """AbsoluteActivity""",
      "output": """{"output":{
"name": "Absolute Activity",
"alternative_labels": [
"Thermodynamic Activity",
]
}
}"""},
     {"input": """OperatingTime""", "output": """{"output":{
"name": "Operating Time",
"alternative_labels": ["Functional Duration",
"System Run Time",
"Equipment Operating Duration",
]
}
}"""},
     {"input": """Concentration""",
      "output": """{"output": {
"name": "Concentration",
"alternative_labels": [
"Volumetric Concentration"]
}
}"""}]

PROCESS_ONTOLOGY_ASSISTANT_EXAMPLES = [{"input": """Fabrication""",
                                        "output": """{"output": {
"name": "Fabrication",
"alternative_labels": [
"Manufacturing",
]
}}"""},
                                       {"input": """Stirring""",
                                        "output": """{"output":{
"name": "Stirring",
"alternative_labels": [
"Mixing",
"Solution Stirring",
]
}}"""},
                                       {"input": """Coating""",
                                        "output": """{"output":{
"name": "Coating",
"alternative_labels": ["Surface Coating",
"Film Application",
]
}}"""}]

MATTER_ONTOLOGY_CANDIDATES_EXAMPLES = [
    {"input": """input: ActiveLayer
Candidates: ActiveMaterial, CatalystLayer, GasDiffusionLayer, Electron Transport Layer, Membrane, CatalystLayer, CurrentCollector, Component""",
     "output":
         {"output": {"answer": {"parents_name": "CatalystLayer"}}}},
    {"input": """input: Molybdenumdioxide
candidates:
Molybdenum Oxide, Molybdenum, Oxidant""",
     "output":
         {"output": {"answer": {"child_name": "Molybdenum Oxide"}}}},
    {"input": """input: MembraneElectrodeAssembly
candidates:
Nickel-Based Diamond-Like Carbon Coated Bipolar Plate, Bipolar Plate, Carbon Coated Bipolar Plate, Diamond-Like Carbon Coated Bipolar Plate""",
     "output": {"output": {"answer": None}}}
]

QUANTITY_ONTOLOGY_CANDIDATES_EXAMPLES = [{"input": """Input: ActiveLayer
Candidates: ActiveMaterial, CatalystLayer, GasDiffusionLayer, Electron Transport Layer, Membrane, CatalystLayer, CurrentCollector, Component""",
                                          "output": """{"output":{
{"candidate": "CatalystLayer", "input_is_subclass_of_candidate": false}
}}"""},
                                         {"input": """input: Molybdenumdioxide
candidates:
Molybdenum Oxide, Molybdenum, Oxidant""",
                                          "output": """{"output":{
{"candidate": "Molybdenum Oxide", "input_is_subclass_of_candidate": true}                                   
}}"""},
                                         {"input": """input: MembraneElectrodeAssembly
candidates:
Nickel-Based Diamond-Like Carbon Coated Bipolar Plate, Bipolar Plate, Carbon Coated Bipolar Plate, Diamond-Like Carbon Coated Bipolar Plate""",
                                          "output": """{"output":
false }                                  
"""}
                                         ]

PROCESS_ONTOLOGY_CANDIDATES_EXAMPLES = [{"input": """Input: Electrospinning
Candidates: Spinning, Electrolysis, Dry Spinning, Fabrication""",
                                         "output": """{"output":{
{"candidate": "Fabrication", "input_is_subclass_of_candidate": true}
}}"""}, {
                                            "input": """input: ChemicalVaporDeposition
candidates: AtomicVaporDeposition, Fabrication, Oxidation""",
                                            "output": """{"output":{
{"candidate": "AtomicVaporDeposition", "input_is_subclass_of_candidate": false}                                   
}}"""},
                                        {"input": """input: DryMilling
candidates:
MEAFabrication, FuelCellFabrication, CatalystPreparation""",
                                         "output": """{"output":
false}                                  
"""}
                                        ]

MATTER_ONTOLOGY_CONNECTOR_EXAMPLES = [
    {"input": """Input: PC61BM
Candidates: Fullerene, Material, Polymer, Pt""",
     "output": """{"output": ["Fullerene", "PCBM", "PC61BM"]}"""}, ]

PROCESS_ONTOLOGY_CONNECTOR_EXAMPLES = [
    {"input": """Input: AtomicVaporDeposition
Candidates: ChemicalVaporDeposition, Process, Oxidation""",
     "output": """{"output": ["ChemicalVaporDeposition", "AtomicLayerDeposition"]}"""},
    {"input": """Input: ElectronMicroscopy
Candidates: Measurement, Fabrication, XRD""",
     "output": """{"output": ["Measurement", "Imaging", "Microscopy", "ElectronMicroscopy"]}"""},
]

QUANTITY_ONTOLOGY_CONNECTOR_EXAMPLES = [
    {"input": """
Input: ElectrospinnningVoltage
Candidates: Voltage, ElectrospinningDistance, SpinningSpeed""",
     "output": """{"output": ["Voltage", "ElectrospinningVoltage"]}"""}, ]
