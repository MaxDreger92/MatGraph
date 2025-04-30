MATTER_ONTOLOGY_ASSISTANT_EXAMPLES = [
    {"input": """NickelBasedDiamondLikeCarbonCoatedBipolarPlate""",
     "output": """{"name": "Nickel-Based Diamond-Like Carbon Coated Bipolar Plate","alternative_labels": ["Ni-DLC Coated Bipolar Plate", "Ni-DLC BPP"], "description": "A bipolar plate coated with nickel-based diamond-like carbon for enhanced conductivity and corrosion resistance."}}"""},
    {"input": """NRE211""",
     "output": """{"name": "NRE211","alternative_labels": ["LiNi0.8Mn0.1Co0.1O2", "Nickel-Rich Layered Oxide Cathode"], "description": "A nickel-rich cathode material commonly used in lithium-ion batteries."}}"""},
    {"input": """MembraneElectrodeAssembly""",
     "output": """{"name": "Membrane Electrode Assembly","alternative_labels": ["MEA", "Proton Exchange Membrane Assembly"], "description": "An assembly combining electrodes and proton exchange membrane in fuel cells."}}"""}
]

QUANTITY_ONTOLOGY_ASSISTANT_EXAMPLES = [
    {"input": """AbsoluteActivity""",
     "output": """{"name": "Absolute Activity","alternative_labels": ["Thermodynamic Activity"], "description": "A measure of the effective concentration of a species in thermodynamic processes."}}"""},
    {"input": """OperatingTime""",
     "output": """{"name": "Operating Time","alternative_labels": ["Run Time"], "description": "Duration for which a system or device is actively functioning."}}"""},
    {"input": """Concentration""",
     "output": """{"name": "Concentration","alternative_labels": ["Volumetric Concentration"], "description": "Amount of a substance present in a given volume."}}"""}
]

PROCESS_ONTOLOGY_ASSISTANT_EXAMPLES = [
    {"input": """Fabrication""",
     "output": """{"name": "Fabrication","alternative_labels": ["Manufacturing"], "description": "Process of manufacturing or constructing a product from raw materials."}}"""},
    {"input": """Stirring""",
     "output": """{"name": "Stirring","alternative_labels": ["Mixing"], "description": "Process of mechanically agitating substances to achieve uniform distribution."}}"""},
    {"input": """Coating""",
     "output": """{"name": "Coating","alternative_labels": ["Surface Coating","Film Application"], "description": "Application of a layer or film on the surface of a material."}}"""}
]


MATTER_ONTOLOGY_CANDIDATES_EXAMPLES = [
    {"input": """input: ActiveLayer
Candidates: ActiveMaterial, CatalystLayer, GasDiffusionLayer, Electron Transport Layer, Membrane, CatalystLayer, CurrentCollector, Component""",
     "output": {"output": {"answer": {"parents_name": "CatalystLayer"}}}},
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
                                          "output": """{
{"candidate": "CatalystLayer", "input_is_subclass_of_candidate": false}
}}"""},
                                         {"input": """input: Molybdenumdioxide
candidates:
Molybdenum Oxide, Molybdenum, Oxidant""",
                                          "output": """{
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
                                         "output": """{
{"candidate": "Fabrication", "input_is_subclass_of_candidate": true}
}}"""}, {
                                            "input": """input: ChemicalVaporDeposition
candidates: AtomicVaporDeposition, Fabrication, Oxidation""",
                                            "output": """{
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
