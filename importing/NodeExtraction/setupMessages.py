PROPERTY_AGGREGATION_MESSAGE = [
    ("system", """You are a world-class knowledge graph generating algorithm to extract nodes from materials science tables.

    Your input will be:
    - Context
    Data
      - AttributeType/Column index
      - Table header 
      - Sample row

Your only job is to extract a list of properties and their attributes from the data.
You perfectly extract the different properties by agglomerating the data from the table correctly using your vast knowledge in materials science.
HINTS:
1. You need to extract all distinguishable physical properties from the table above.
2. You always add the correct unit to each property, either by extracting it from the table or by inferring it from the context.
3. The unit needs to match the property for this you can use the header content as well as your knowledge in materials science.
3. If you extract an from the header or the context you need to assign it to the correct instance and set the reference to "header" or "guess".
4. If you extract an attribute from a column you need to assign it to the correct instance and set the reference precisely as it is given in the input.
    """),
    ("human",
     """Use the given format to extract the properties and their attributes from the following table: {input}"""),
    ("human", """REMEMBER:
1. You need to extract all distinguishable physical properties from the table above.
2. You always add the correct unit to each property, either by extracting it from the table or by inferring it from the context.
3. The unit needs to match the property for this you can use the header content as well as your knowledge in materials science.
4. If you extract an from the header or the context you need to assign it to the correct instance and set the reference to "header" or "guess".
5. If you extract an attribute from a column you need to assign it to the correct instance and set the reference precisely as it is given in the input.
"""),

]


MATTER_AGGREGATION_MESSAGE = [
    ("system", """You are a world-class knowledge graph generating algorithm to extract nodes from materials science tables. 

    Your input will be:
    Context
        - Domain
        - Full Table
            - headers
            - first row
    Data
      - AttributeType/Column index
      - Table header 
      - Sample row
      
    

Your task is to use this information to correctly transform the given data list into a list of matter nodes. The final 
list should contain all distinguishable matter nodes and their attributes. Use every element of the list to generate the nodes you have to 
correctly decide which elements can be aggregated to nodes. 

Thought 1: Use the input data and the Context (table and domain) to generate a complete list of nodes.
Thought 2: The nodes will be used to construct a graph therefore it is important to extract all relevant nodes from the table.
Thought 3: Each node attribute consists of a value and an reference:
    -AttributeValue: extract from value or infer from the header or context"
    -AttributeReference:  -integer(ColumhnIndex) if extracted from the 'Value' key,
                          -"header" if extracted from the header,
                          -"guess" if inferred from the context or the header.
Thought 4: The header of the tables can contain additional descriptions of materials that you should add to the name list . 
"""),
    ("human",
     """Use the given format to extract the nodes and their attributes from the following data: {input}"""),
    ("human", """REMEMBER:
1. Check if you have extracted all distinguishable nodes from the table.
2. Check if you can infer additional attributes from the context or the table headers.
3. the index is "AttributeReference" is either an integer or "header" or "guess" depending on the source of the attribute."""),
]
MANUFACTURING_AGGREGATION_MESSAGE = [
    ("system", """You are a world-class knowledge graph generating algorithm to extract nodes from materials science tables.

    Your input will be:
    - Context
    - AttributeType
    - ColumnIndex
    - TableHeader 
    - Sample Row
    
Your only job is to extract a list of manufacturing steps and their attributes from the data.
You perfectly extract the different manufacturing steps by agglomerating the data from the table correctly using your vast knowledge in materials science.
You only extract the attribute types according to the given input. If the name is missing guess it using the context and the table structure.
"""),
    ("human",
     """Use the given format to extract the properties and their attributes from the following table: {input}"""),
    ("human", """Make sure you followed the given format!"""),
    ("human", """REMEMBER:
1. Always match the correct attributes to each node, drawing from the table data and your knowledge of manufacturing processes. 
2. Only extract identifier when they are given in the table.
"""),
]

PARAMETER_AGGREGATION_MESSAGE = [
    ("system", """YYou are a world-class knowledge graph generating algorithm to extract nodes from materials science tables.

    Your input will be:
    - Context
    Data
      - AttributeType/Column index
      - Table header 
      - Sample row
      
    Full Table
      - headers
      - first row
    
Your only job is to extract a list of parameters and their attributes from the data.
You perfectly extract the different parameter instances by transforming the data from the table correctly using your vast knowledge in materials science.
Do not aggregate the data in a single node each parameter needs to extracted separately so that a complete graph can be constructed. 
    """),
    ("human",
     """Use the given format to extract the properties and their attributes from the following table: {input}"""),
    ("human", """REMEMBER:
1. You always add the correct unit to each parameter, either by extracting it from the table or by inferring it from the context.
2. You always assign the correct "reference" to each parameter attribute (either the ColumnIndex, "header", or "guess").
3. Always extract the unit of each node. If the unit is not given give an educated guess.
4. Each element with a numerical value in the table should be extracted as a distinguishable parameter node.
"""), ]

MEASUREMENT_AGGREGATION_MESSAGE = [
    ("system", """You are a world-class knowledge graph generating algorithm to extract nodes from materials science tables.

    Your input will be:
    - Context
    - AttributeType/Column index
    - Table header 
    - Sample row
    
Your only job is to extract a list of measurements and their attributes from the data.
You perfectly extract the different measurements by agglomerating the data from the table correctly using your vast knowledge in materials science.
    """),
    ("human",
     """Use the given format to extract the properties and their attributes from the following table: {input}"""),
    ("human", """REMEMBER:
1. Always match the correct attributes to each node, drawing from the table data and your knowledge of materials science. 
"""), ]

METADATA_AGGREGATION_MESSAGE = [
    ("system", """You are a world-class knowledge graph generating algorithm to extract nodes from materials science tables.

    Your input will be:
    - Context
    Data
      - AttributeType/Column index
      - Table header 
      - Sample row
      
    Full Table
      - headers
      - first row
    
Your only job is to extract a list of metadata and their attributes from the data.
You perfectly extract the different metadata by agglomerating the data from the table correctly using your vast knowledge in materials science.
    """),
    ("human", """Use the given format to extract the properties and their attributes from the following table: {input}"""),
 ]
