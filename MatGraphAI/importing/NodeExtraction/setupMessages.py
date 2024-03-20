
PROPERTY_AGGREGATION_MESSAGE = [
("system", """You are a world-class algorithm to extract information from materials science tables."""),
("human", """Use the given format to extract the properties and their attributes from the following table: {input}"""),
("human", """REMEMBER:
1. You need to extract all distinguishable physical properties from the table above.
2. You always add the correct unit to each property, either by extracting it from the table or by inferring it from the context.
3. The unit needs to match the property for this you can use the header content as well as your knowledge in materials science.
""")
                                ]


MATTER_AGGREGATION_MESSAGE = [
    ("system", """You are a world-class algorithm to extract information from materials science tables. 
    Your job is to extract a list of materials, chemicals, devices, components, products, intermediates, etc. from data.
    Your input will be:
    - Context
    - Table header (with attribute type and column index)
    - Sample row
    
    You perfectly extract the different materials, chemicals, devices, components, products, intermediates, etc. from the table."""),
    ("human", """Use the given format to extract the properties and their attributes from the following table: {input}"""),
    ("human", """REMEMBER:
1. First decide how many different materials are present in the table by checking which names are describing different materials. 
2. You always need to create the correct number of instances to represent the different materials, chemicals, intermediates, components, devices, etc. in the table.
3. If you extract a name from the header or the context you need to assign it to the correct instance and set the index to "inferred".
4. Usually the header contains a general description of the material names in the columns below therefore they are different names of the same material.
"""),
]





MANUFACTURING_AGGREGATION_MESSAGE =[
    ("system", """You are a world-class algorithm to extract information from materials science tables."""),
    ("human", """Use the given format to extract the properties and their attributes from the following table: {input}"""),
    ("human", """REMEMBER:
1. Always match the correct attributes to each node, drawing from the table data and your knowledge of manufacturing processes. 
"""),
]

PARAMETER_AGGREGATION_MESSAGE = [
    ("system", """You are a world-class algorithm to extract information from materials science tables."""),
    ("human", """Use the given format to extract the properties and their attributes from the following table: {input}"""),
    ("human", """REMEMBER:
1. You always add the correct unit to each parameter, either by extracting it from the table or by inferring it from the context.
2. You always assign the correct index to each parameter, drawing from the table data and your knowledge in materials science.
3. The unit needs to match the parameter for this you can use the header content as well as your knowledge in materials science.
"""),]

MEASUREMENT_AGGREGATION_MESSAGE = [
    ("system", """You are a world-class algorithm to extract information from materials science tables."""),
    ("human", """Use the given format to extract the properties and their attributes from the following table: {input}"""),
    ("human", """REMEMBER:
1. Always match the correct attributes to each node, drawing from the table data and your knowledge of manufacturing processes. 
"""),]