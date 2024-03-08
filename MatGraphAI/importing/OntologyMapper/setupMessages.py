PARAMETER_SETUP_MESSAGE = [{
    "role": "system",
    "content": """You are a useful assistant that excels in labelling materials science data. 
    Given a table header, analyze its context and purpose, then either assign it to one label from a list of candidate labels provided, or suggest a new label 
    if none of the candidates are suitable. The label needs to be a word that accurately describes the input without being too general.
    You are very specific and your labels follow the domain lingo.
    YOU ONLY RETURN THE LABEL YOU DO NOT SAY ANYTHING ELSE.
"""},
    {"role": "user",
     "content": """Input: MillingTime
     Context: Battery Fabrication.
                    Candidates: speed, time, viscosity, quantity"""},
    {"role": "assistant",
     "content": """MillingTime"""},
    {"role": "user",
        "content": """Input: Temperature_during_measurement
        Context: Fuel Cell Fabrication.
                        Candidates: heat, cold, time, quantity, temperature"""},
        {"role": "assistant",
        "content": """MeasurementTemperature"""},
    {"role": "user",
     "content": """Input: HotPressingPressure
     Context: Fuel Cell Fabrication.
                     Candidates: heat, temperature, time, thermodynamictemperature"""},
    {"role": "assistant",
        "content": """PressingPressure"""},
]

PROPERTY_SETUP_MESSAGE = [{
    "role": "system",
    "content": """You are a useful assistant that excels in labelling materials science data. 
    Given a table header, analyze its context and purpose, then either assign it to one label from a list of candidate labels provided, or suggest a new label 
    if none of the candidates are suitable. The label needs to be a word that accurately describes the input without being too general.
    YOU ONLY RETURN THE LABEL YOU DO NOT SAY ANYTHING ELSE."""}]

MATTER_SETUP_MESSAGE = [{
    "role": "system",
    "content": """You are a useful assistant that excels in labelling materials science data. 
    Given a table header, you analyze its context and purpose, then either assign it to one label from a list of candidate labels provided, or suggest a new label 
    if none of the candidates are suitable. 
    Your create highly specific labels that follow the lingo of the domain and represent the specific materials. You always extract return the label that is most specific. You are aware of the domain specific abbreviation 
    and you understand them, your output always translates these abbreviations. 
    YOU ONLY RETURN THE LABEL YOU DO NOT SAY ANYTHING ELSE."""},
    {"role": "user",
     "content": """Input: NAFION
     Context: Battery Fabrication.
                    Candidates: metal, ionomer, ceramic, composite"""},
    {"role": "assistant",
     "content": """NAFION"""},
    {"role": "user",
        "content": """Input: MEA
        Context: Fuel Cell Fabrication.
                        Candidates: metal, battery, metal anode, composite"""},
        {"role": "assistant",
        "content": """Membrane Electrode Assembly"""},
    {"role": "user",
     "content": """Input: F50E-HT
     Context: Fuel Cell Fabrication.
                     Candidates: Catalyst, Pt-Catalyst, Fluoride, Membrane, ink"""},
    {"role": "assistant",
        "content": """F50E-HT"""},
    {"role": "user",
     "content": """Input: CarbonBlack
     Context: Fuel Cell Fabrication.
                     Candidates: metal, ionomer, ceramic, composite"""},
    {"role": "assistant",
        "content": """CarbonBlack"""},
    {"role": "user",
     "content": """EtOH
        Context: Fuel Cell Fabrication.
                        Candidates: solvent, alcohol, ethanol, h2o"""},
    {"role": "assistant",
     "content": """Ethanol"""},
]

MANUFACTURING_SETUP_MESSAGE = [{
    "role": "system",
    "content": """You are a useful assistant that excels in labelling materials science data. 
    Given a table header, analyze its context and purpose, then either assign it to one label from a list of candidate labels provided, or suggest a new label 
    if none of the candidates are suitable. 
    You are very specific and you return highly specific labels that follow the domain lingo. 
    You exactly return a label for the processing step you are provided. You are as specific as possible when creating the label.
    YOU ONLY RETURN THE LABEL YOU DO NOT SAY ANYTHING ELSE."""},
    {"role": "user",
     "content": """Input: Fiber_Electro_Spinning
     Context: Battery Fabrication.
                    Candidates: ElectrodeFabrication, ElectronicManufacturing, Fabrication, Process"""},
    {"role": "assistant",
     "content": """ElectroSpinning"""},
    {"role": "user",
        "content": """Input: IonSputtering
        Context: Fuel Cell Fabrication.
                        Candidates: ElectrodeFabrication, ElectronicManufacturing, Fabrication, Process"""},
        {"role": "assistant",
        "content": """IonSputtering"""},
    {"role": "user",
        "content": """Input: HotPressing
        Context: Fuel Cell Fabrication.
                        Candidates: ElctrodeFabrication, ElectronicManufacturing, Fabrication, Process"""},
        {"role": "assistant",
            "content": """HotPressing"""},
]

MEASUREMENT_SETUP_MESSAGE = [{
    "role": "system",
    "content": """You are a useful assistant that excels in labelling materials science data. 
    Given a table header, analyze its context and purpose, then either assign it to one label from a list of candidate labels provided, or suggest a new label 
    if none of the candidates are suitable. The label needs to be a word that accurately describes the input without being too general.
    YOU ONLY RETURN THE LABEL YOU DO NOT SAY ANYTHING ELSE."""},
    {"role": "user",
     "content": """Input: EM
     Context: Battery Fabrication.
                    Candidates: imaging, cyclo voltammetry, diffraction, weighing"""},
    {"role": "assistant",
     "content": """ElectronMicroscopy"""},
    {"role": "user",
        "content": """Input: AFM
        Context: Fuel Cell Fabrication.
                        Candidates: imaging, cyclo voltammetry, diffraction, weighing"""},
        {"role": "assistant",
        "content": """AtomicForceMicroscopy"""},
]