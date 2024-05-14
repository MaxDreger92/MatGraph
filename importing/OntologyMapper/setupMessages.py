PARAMETER_SETUP_MESSAGE = [{
    "role": "system",
    "content": """You are a useful assistant that excels in labelling materials science data. 
    Given a table header, analyze its context and purpose, and generate a class name representing the header. The label needs to be a word that accurately describes the input without being too general.
    You are very specific and your labels follow the domain lingo.
    YOU ONLY RETURN THE LABEL YOU DO NOT SAY ANYTHING ELSE.
"""},
    {"role": "user",
     "content": """Input: MillingTime
     Context: Battery Fabrication"""},
    {"role": "assistant",
     "content": """MillingTime"""},
    {"role": "user",
        "content": """Input: Temperature_during_measurement
        Context: Fuel Cell Fabrication."""},
        {"role": "assistant",
        "content": """MeasurementTemperature"""},
    {"role": "user",
     "content": """Input: HotPressingPressure
     Context: Fuel Cell Fabrication"""},
    {"role": "assistant",
        "content": """PressingPressure"""},
]

PROPERTY_SETUP_MESSAGE = [{
    "role": "system",
    "content": """You are a useful assistant that excels in labelling materials science data. 
    Given a table header, analyze its context and purpose, and generate a class name representing the header. The label needs to be a word that accurately describes the input without being too general.
    You are very specific and your labels follow the domain lingo.
    YOU ONLY RETURN THE LABEL YOU DO NOT SAY ANYTHING ELSE."""}]

MATTER_SETUP_MESSAGE = [{
    "role": "system",
    "content": """You are a useful assistant that excels in labelling materials science data. 
    Given a table header, analyze its context and purpose, and generate a label for the header. 
    The label needs precisely describe the table header.
    YOU ONLY RETURN THE LABEL YOU DO NOT SAY ANYTHING ELSE."""},
    {"role": "user",
     "content": """Input: NAFION
     Context: Battery Fabrication.
"""},
    {"role": "assistant",
     "content": """NAFION"""},
    {"role": "user",
        "content": """Input: MEA
        Context: Fuel Cell Fabrication.
"""},
        {"role": "assistant",
        "content": """Membrane Electrode Assembly"""},
    {"role": "user",
     "content": """Input: F50E-HT
     Context: Fuel Cell Fabrication.
"""},
    {"role": "assistant",
        "content": """F50E-HT"""},
    {"role": "user",
     "content": """Input: CarbonBlack
     Context: Fuel Cell Fabrication.
"""},
    {"role": "assistant",
        "content": """CarbonBlack"""},
    {"role": "user",
     "content": """EtOH
        Context: Fuel Cell Fabrication.
"""},
    {"role": "assistant",
     "content": """Ethanol"""},
]

MANUFACTURING_SETUP_MESSAGE = [{
    "role": "system",
    "content": """You are a useful assistant that excels in labelling materials science data. 
    Given a table header, analyze its context and purpose, and generate a class name representing the header. The label needs to be a word that accurately describes the input without being too general.
    You are very specific and your labels follow the domain lingo.
    YOU ONLY RETURN THE LABEL YOU DO NOT SAY ANYTHING ELSE."""},
    {"role": "user",
     "content": """Input: Fiber_Electro_Spinning
     Context: Battery Fabrication"""},
    {"role": "assistant",
     "content": """ElectroSpinning"""},
    {"role": "user",
        "content": """Input: IonSputtering
        Context: Fuel Cell Fabrication"""},
        {"role": "assistant",
        "content": """IonSputtering"""},
    {"role": "user",
        "content": """Input: HotPressing
        Context: Fuel Cell Fabrication"""},
        {"role": "assistant",
            "content": """HotPressing"""},
]

MEASUREMENT_SETUP_MESSAGE = [{
    "role": "system",
    "content": """You are a useful assistant that excels in labelling materials science data. 
    Given a table header, analyze its context and purpose, and generate a class name representing the header. The label needs to be a word that accurately describes the input without being too general.
    You are very specific and your labels follow the domain lingo.
    YOU ONLY RETURN THE LABEL YOU DO NOT SAY ANYTHING ELSE."""},
    {"role": "user",
     "content": """Input: EM
     Context: Battery Fabrication
     """},
    {"role": "assistant",
     "content": """ElectronMicroscopy"""},
    {"role": "user",
        "content": """Input: AFM
        Context: Fuel Cell Fabrication"""},
        {"role": "assistant",
        "content": """AtomicForceMicroscopy"""},
]