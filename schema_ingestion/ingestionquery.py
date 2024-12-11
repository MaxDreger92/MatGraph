import os

from neomodel import db


def get_query(file_path):
    file_path = file_path.replace("\\", "/")
    return [f"""
    // Step 1: Load the initial CSV and create nodes
    LOAD CSV WITH HEADERS FROM 'file:///{file_path}/org.csv' AS row FIELDTERMINATOR ';'
    WITH row, SPLIT(row.Author,"\n") AS authors, SPLIT(row.ORCID,"\n") AS orcids, SPLIT(row.Email,"\n") AS emails
    
    MERGE (HIP:Metadata:FoundingBody  {{name:row.FoundingBody, identifier: 546546}})
    ON CREATE SET HIP.uid = RandomUUID()

    MERGE (test_exp:Process:Experiment  {{identifier:row.ExperimentID, date_added:row.UploadDate }})
    ON CREATE set test_exp.uid = RandomUUID()
    MERGE (test_exp) -[:HAS_FOUNDER]-> (HIP)
    MERGE (ForschungszentrumJuelich:Metadata:Institution  {{name:row.Institution}})
    ON CREATE SET ForschungszentrumJuelich.uid = RandomUUID()
    MERGE (test_exp)-[:PUBLISHED_BY]->(ForschungszentrumJuelich)
    MERGE (Germany:Metadata:Country {{name:row.Country}})
    ON CREATE SET Germany.uid = RandomUUID()
    MERGE (ForschungszentrumJuelich)-[:IN]->(Germany)
    MERGE (RSC:Metadata:Publication  {{name:row.Publication, published:row.Published, doi:row.DOI, journal:row.Journal,volume: row.Volume, issue: row.Issue, pages: row.Pages, publishing_date: row.PublicationDate}})
    ON CREATE SET RSC.uid = RandomUUID()
    MERGE (test_exp)-[:PUBLISHED_IN]->(RSC)
    
    MERGE (tags_exp:Metadata:Tags {{topic: row.Topic, device:row.Device}})
    ON CREATE SET tags_exp.uid = RandomUUID()
    MERGE (test_exp)-[:TAGGED_AS]->(tags_exp)
    MERGE (exp_pics:Metadata:File {{name: row.FileName}})
    ON CREATE SET exp_pics.uid = RandomUUID()
    SET exp_pics += apoc.map.clean({{
        format: row.Format,
        link: row.Link,
        file_size: row.FileSize,
        dimension_x: row.DimensionX,
        dimension_y: row.DimensionY,
        dimension_z: row.DimensionZ,
        px_per_metric: row.PixelPerMetric,
        mask_exist: row.MaskExist,
        mask_link: row.MaskLink
    }}, [], [null])    
    CREATE (test_exp)-[:HAS]->(exp_pics)
    MERGE (sample_preparation_process:Manufacturing:Process  {{name: 'SamplePreparation', identifier:row.ExperimentID}})
    ON CREATE SET sample_preparation_process.uid = RandomUUID()
    MERGE (test_exp)-[:HAS_PROCESS]->(sample_preparation_process)
    MERGE (synthesis_process:Manufacturing:Process  {{name: 'Synthesis', identifier:row.ExperimentID}})
    ON CREATE SET synthesis_process.uid = RandomUUID()
    MERGE (test_exp)-[:HAS_PROCESS]->(synthesis_process)
    
    WITH row,test_exp, RSC, authors, orcids, emails, sample_preparation_process
    // Loop over the authors and orcids lists 
    UNWIND range(0, size(authors) - 1) AS idx 
    WITH row,test_exp, RSC, authors[idx] AS author, orcids[idx] AS orcid, emails[idx] AS email, sample_preparation_process
    // Create or merge the Author nodes with corresponding ORCID properties 
    MERGE (a:Metadata:Author  {{name: author}}) 
    ON CREATE SET a.orcid = orcid
    ON CREATE SET a.uid = RandomUUID() 
    ON CREATE SET a.email = email
    MERGE (a)-[:IS_AUTHOR]->(RSC)
    MERGE (a)-[:CONDUCTED]->(test_exp)
    
    WITH test_exp, sample_preparation_process
    // Step 2: Load the second CSV and create nodes
    LOAD CSV WITH HEADERS FROM 'file:///{file_path}/sp.csv' AS row1 FIELDTERMINATOR ';'
    WITH row1, sample_preparation_process, SPLIT(row1.Condition, "\n") AS conditions,SPLIT(row1.AmountPrecursor, ' ') AS precursorAmountParts, SPLIT(row1.AmountTarget, ' ') AS targetAmountParts
    
    ORDER BY toInteger(row1.Step) // Ensure rows are processed in order of steps
    
    // Create or merge nodes for subprocess, component, target, and condition
    MERGE (subprocess1:Manufacturing:Process  {{name: row1.Technique, identifier: row1.ExperimentID, step: toInteger(row1.Step)}})
    ON CREATE SET subprocess1.uid = RandomUUID(),
    subprocess1.isNew = true
    MERGE (component1:Matter  {{name: row1.Precursor, identifier: row1.ExperimentID}})-[:HAS_PROPERTY]->(amount:Property 
    {{name: 'amount'}})
    ON CREATE SET 
        component1.uid = RandomUUID(),
        amount.uid = RandomUUID(),
        amount.unit = CASE WHEN size(precursorAmountParts) > 1 THEN precursorAmountParts[1] ELSE "NA" END,
        amount.value = apoc.number.parseFloat(precursorAmountParts[0])

    MERGE (target1:Matter  {{name: row1.Target, identifier: row1.ExperimentID}})-[:HAS_PROPERTY]->(amount1:Property 
    {{name: 'amount'}})
    ON CREATE SET 
        target1.uid= RandomUUID(),
        amount1.uid = RandomUUID(),
        amount1.uid = CASE WHEN size(targetAmountParts) > 1 THEN targetAmountParts[1] ELSE "NA" END,
        amount1.value = apoc.number.parseFloat(targetAmountParts[0])
    
    MERGE (sample_preparation_process)-[:HAS_PART]->(subprocess1)
    MERGE (component1)-[:IS_MANUFACTURING_INPUT]->(subprocess1)
    MERGE (subprocess1)-[:HAS_MANUFACTURING_OUTPUT]->(target1)
    
    WITH row1, conditions, subprocess1, target1 ,sample_preparation_process
    // Extract key-value pairs from the Condition field
    UNWIND conditions AS condition
    WITH row1, condition, subprocess1, target1, sample_preparation_process
    WHERE condition CONTAINS '='
    WITH row1, subprocess1, sample_preparation_process,target1, trim(SPLIT(condition, '=')[0]) AS key, trim(SPLIT(condition, '=')[1]) AS value
    WITH row1, subprocess1,sample_preparation_process,target1, key, SPLIT(value, ' ')[0] AS number, SPLIT(value, ' ')[1] AS unit, value
    WITH row1, subprocess1, sample_preparation_process,target1 ,key, value, number, unit,    
        CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN apoc.number.parseFloat(number) ELSE value END AS parsed_value,
        CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN unit ELSE NULL END AS parsed_unit
    // Use APOC to dynamically create Parameter nodes and set properties
    // Check if the value part is a number and create the appropriate node and relationships
    
    CALL apoc.do.when(
    subprocess1.isNew IS NOT NULL,
    '
    // Create the Parameter node
    CREATE (param:Parameter  {{uid:RandomUUID()}})
    
    // Conditionally set the key-value property if the value is numeric
    FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN [1] ELSE [] END |
        SET param.name = key,param.value = number,param.unit = unit
    
    )
    
    // Conditionally set the key-value property if the value is not numeric
    FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NULL THEN [1] ELSE [] END |
        SET param.name = key, param.value = value 
    )
    
    MERGE (subprocess1)-[:HAS_PARAMETER]->(param)
    RETURN NULL
    ',
    '',
  {{
    subprocess1: subprocess1,
    key: key,
    value: value,
    number:number,
    unit: unit
  }}
) YIELD value AS thing
    REMOVE subprocess1.isNew
    // Carry forward data for comparison in the next step
    WITH row1, subprocess1, target1
    ORDER BY toInteger(row1.Step)
    
    // Match the next step and check if the target of the current step is used as a precursor in the next step
    MATCH (next_row1  {{ExperimentID: row1.ExperimentID, step: toInteger(row1.Step) + 1}})
    WITH row1, subprocess1, target1, next_row1
    
    // Compare target and precursor names
    WHERE target1.name = next_row1.Precursor
    MERGE (target1)-[:IS_MANUFACTURING_INPUT]->(subprocess1);
    """,
    f"""    
    // Step 3: Ensure the synthesis_process node exists
    // Load the third CSV file
    LOAD CSV WITH HEADERS FROM 'file:///{file_path}/syn.csv' AS row2 FIELDTERMINATOR ';'
    WITH row2, SPLIT(row2.Condition, "\n") AS conditions,SPLIT(row2.AmountPrecursor, ' ') AS precursorAmountParts, SPLIT(row2.AmountTarget, ' ') AS targetAmountParts
    ORDER BY toInteger(row2.Step) // Ensure rows are processed in order of steps
    
    // Create or merge nodes for subprocess, component, target, and condition
    MERGE (synthesis_process:Manufacturing:Process  {{name: 'Synthesis', identifier:row2.ExperimentID}})
    ON CREATE SET synthesis_process.uid = RandomUUID() 
    MERGE (subprocess2:Manufacturing:Process  {{name: row2.Technique, identifier: row2.ExperimentID, step: toInteger(row2.Step)}})
    ON CREATE SET subprocess2.uid = RandomUUID(), 
    subprocess2.isNew = true
    MERGE (component2:Matter  {{name: row2.Precursor, identifier: row2.ExperimentID}})-[:HAS_PROPERTY]->(component2amount:Property {{name: 'amount'}})

    ON CREATE SET 
        component2.uid = RandomUUID() ,
        component2amount.value = apoc.number.parseFloat(precursorAmountParts[0]),
        component2amount.unit = CASE WHEN size(precursorAmountParts) > 1 THEN precursorAmountParts[1] ELSE NULL END
    MERGE (target2:Matter  {{name: row2.Target, identifier: row2.ExperimentID}})-[:HAS_PROPERTY]->(target2amount:Property {{name: 'amount'}})
    ON CREATE SET 
        target2.uid = RandomUUID(), 
        target2amount.value = apoc.number.parseFloat(targetAmountParts[0]),
        target2amount.unit = CASE WHEN size(targetAmountParts) > 1 THEN targetAmountParts[1] ELSE NULL END
    
    MERGE (synthesis_process)-[:HAS_PART]->(subprocess2)
    MERGE (component2)-[:IS_MANUFACTURING_INPUT]->(subprocess2)
    MERGE (subprocess2)-[:HAS_MANUFACTURING_OUTPUT]->(target2)
    
    WITH row2, conditions, subprocess2, target2 ,synthesis_process
    // Extract key-value pairs from the Condition field
    UNWIND conditions AS condition
    WITH row2, condition, subprocess2,target2 ,synthesis_process
    WHERE condition CONTAINS '='
    WITH row2, subprocess2, synthesis_process,target2, trim(SPLIT(condition, '=')[0]) AS key, trim(SPLIT(condition, '=')[1]) AS value
    WITH row2, subprocess2,synthesis_process,target2, key, SPLIT(value, ' ')[0] AS number, SPLIT(value, ' ')[1] AS unit, value
    WITH row2, subprocess2,synthesis_process,target2 ,key, value, number, unit,    
        CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN apoc.number.parseFloat(number) ELSE value END AS parsed_value,
        CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN unit ELSE NULL END AS parsed_unit
    // Use APOC to dynamically create Parameter nodes and set properties
    // Check if the value part is a number and create the appropriate node and relationships
    
    // Create the Parameter node
    // Use FOREACH for conditional execution without a subquery
    FOREACH (_ IN CASE WHEN subprocess2.isNew THEN [1] ELSE [] END |
      
      // Create the Parameter node
      CREATE (param:Parameter {{name: key, uid: RandomUUID()}})
      
      // Conditionally set properties
      FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN [1] ELSE [] END |
        SET param.value = number,
            param.unit = unit
      )
      FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NULL THEN [1] ELSE [] END |
        SET param.value = value
      )

      
      // Create the relationship
      MERGE (subprocess2)-[:HAS_PARAMETER]->(param)
    )
    
    REMOVE subprocess2.isNew
    // Carry forward data for comparison in the next step
    WITH row2, synthesis_process, subprocess2, target2
    ORDER BY toInteger(row2.Step)
    
    // Match the next step and check if the target of the current step is used as a precursor in the next step
    MATCH (next_row2  {{ExperimentID: row2.ExperimentID, step: toInteger(row2.Step) + 1}})
    WITH row2, synthesis_process, subprocess2, target2, next_row2
    
    // Compare target and precursor names
    WHERE target2.name = next_row2.Precursor
    MERGE (target2)-[:IS_MANUFACTURING_INPUT]->(subprocess2);
    """,
    f"""    
    //Step4: Loading Characterization Method
    
    // Load the fourth CSV file
    LOAD CSV WITH HEADERS FROM 'file:///{file_path}/char.csv' AS row3 FIELDTERMINATOR ';'
    WITH row3
    ORDER BY toInteger(row3.Step) // Ensure rows are processed in order of steps
    MERGE (test_exp:Experiment:Process  {{identifier:row3.ExperimentID }})
    ON CREATE SET 
    test_exp.uid = RandomUUID() 
    // Merge or create the characterization node
MERGE (characterization:Measurement:Process {{method: row3.MeasurementMethod, measurement_type: row3.MeasurementType, specimen: row3.Specimen, identifier: row3.ExperimentID}})
ON CREATE SET characterization.uid = RandomUUID(), characterization.isNew = true

// Create the relationship to test_exp (ensure test_exp is defined)
MERGE (test_exp)-[:HAS_PROCESS]->(characterization)

WITH characterization, test_exp, row3

// Proceed only if characterization was newly created
FOREACH (_ IN CASE WHEN characterization.isNew THEN [1] ELSE [] END |

// Create the Sample node and relationship
CREATE (sample:Matter {{name: 'Sample', identifier: row3.ExperimentID, uid: RandomUUID()}})
MERGE (sample)-[:IS_MEASUREMENT_INPUT]->(characterization)

                                        // Create the parameter nodes
CREATE (temperature2:Parameter {{uid: RandomUUID(), name: 'Temperature', value: row3.Temperature, unit: row3.TemperatureUnit}})
CREATE (humidity:Parameter {{uid: RandomUUID(), name: 'Humidity', value: row3.Humidity, unit: row3.HumidityUnit}})
CREATE (atmosphere:Parameter {{uid: RandomUUID(), name: 'Atmosphere', value: row3.Atmosphere, unit: row3.AtmosphereUnit}})
CREATE (pressure:Parameter {{uid: RandomUUID(), name: 'Pressure', value: row3.Pressure, unit: row3.PressureUnit}})

// Create relationships between characterization and parameter nodes
CREATE (characterization)-[:HAS_PARAMETER]->(temperature2)
CREATE (characterization)-[:HAS_PARAMETER]->(humidity)
CREATE (characterization)-[:HAS_PARAMETER]->(atmosphere)
CREATE (characterization)-[:HAS_PARAMETER]->(pressure)

                                            // Create the calibration parameter
CREATE (calibration:Parameter {{uid: RandomUUID(), name: 'Calibration', value: row3.Calibration}})
CREATE (characterization)-[:HAS_PARAMETER]->(calibration)

                                            // Create the raw data node and relationship
CREATE (raw_data:Data {{uid: RandomUUID(), name: 'RawData', identifier: row3.ExperimentID, link: 'link'}})
CREATE (characterization)-[:HAS_MEASUREMENT_OUTPUT]->(raw_data)
)


    """,
    f"""    
LOAD CSV WITH HEADERS FROM 'file:///{file_path}/inst.csv' AS row FIELDTERMINATOR ';'
MERGE (characterization:Measurement:Process {{identifier:row.ExperimentID}})
ON CREATE SET characterization.uid = RandomUUID(),
              characterization.isNew = true
WITH *
CALL apoc.do.when(
  characterization.isNew IS NOT NULL,
  '
    CALL apoc.create.node(["Instrument"], apoc.map.fromPairs([key IN keys($row) | [key, $row[key]]])) YIELD node as instrument
    SET instrument.uid = RandomUUID()
    SET instrument:Instrument
    MERGE (characterization)-[:BY_INSTRUMENT]->(instrument)
    RETURN true
  ',
  '
    RETURN true
  ',
  {{row: row, characterization: characterization}}
) YIELD value AS stuff
REMOVE characterization.isNew
    """,
    f"""    
    // Step 5: Image preprocessing
    // Load the fifth CSV file
    LOAD CSV WITH HEADERS FROM 'file:///{file_path}/pre.csv' AS row2 FIELDTERMINATOR ';'
    WITH row2,SPLIT(row2.Condition, "\n") AS conditions, SPLIT(row2.Software, "\n") AS softwares,SPLIT(row2.AmountPrecursor, ' ') AS precursorAmountParts, SPLIT(row2.AmountTarget, ' ') AS targetAmountParts
    ORDER BY toInteger(row2.Step) // Ensure rows are processed in order of steps
    
    MERGE (test_exp:Experiment  {{identifier:row2.ExperimentID }})
    ON CREATE SET 
    test_exp.uid = RandomUUID()
    MERGE (preprocessing:DataProcessing:Process {{name:"DataPreprocessing", identifier:row2.ExperimentID}})
    ON CREATE SET
    preprocessing.uid = RandomUUID()
    MERGE (test_exp)-[:HAS_PROCESS]->(preprocessing)
    // Create or merge nodes for subprocess, component, target, and condition
    MERGE (subprocess2:DataProcessing:Process  {{name: row2.Technique, identifier: row2.ExperimentID, step: toInteger(row2.Step)}})
    ON CREATE SET subprocess2.uid = RandomUUID(),
    subprocess2.isNew = false
    MERGE (component2:Data  {{name: row2.Precursor, identifier: row2.ExperimentID}})
    ON CREATE SET 
        component2.uid = RandomUUID(),
        component2.value = apoc.number.parseFloat(precursorAmountParts[0]),
        component2.unit = CASE WHEN size(precursorAmountParts) > 1 THEN precursorAmountParts[1] ELSE NULL END
    MERGE (target2:Data  {{name: row2.Target, identifier: row2.ExperimentID}})
    ON CREATE SET 
        target2.uid = RandomUUID(),
        target2.amount = apoc.number.parseFloat(targetAmountParts[0]),
        target2.unit = CASE WHEN size(targetAmountParts) > 1 THEN targetAmountParts[1] ELSE NULL END
    
    MERGE (preprocessing)-[:HAS_PART]->(subprocess2)
    MERGE (component2)-[:IS_DATAPROCESSING_INPUT]->(subprocess2)
    MERGE (subprocess2)-[:HAS_DATAPROCESSING_OUTPUT]->(target2)
    
    WITH row2, preprocessing, subprocess2, target2, softwares, conditions
    UNWIND softwares AS software
    WITH row2, subprocess2, target2, preprocessing, software, conditions
    WHERE software CONTAINS '='
    WITH row2, subprocess2,target2, preprocessing, trim(SPLIT(software, '=')[0]) AS key, trim(SPLIT(software, '=')[1]) AS value, conditions
    // Carry forward data for comparison in the next step
    // Proceed only if subprocess2 was newly created
CALL apoc.do.when(
  subprocess2.isNew IS NOT NULL,
  '
    MATCH (sp)
    WHERE id(sp) = $subprocess2Id
    CREATE(soft:Metadata {{uid: RandomUUID()}}
    WITH *
    CALL apoc.create.setProperties(soft, [$key], [$value]) YIELD node AS updated_soft
    SET updated_soft.name = updated_soft.Software
    REMOVE updated_soft.Software
    MERGE (sp)-[:HAS_PARAMETER]->(updated_soft)
    RETURN null
  ',
  '',
  {{
    subprocess2Id: id(subprocess2),
    key: key,
    value: value
  }}
) YIELD value AS thing

// Continue with the rest of your query
    
    WITH row2, conditions, subprocess2, preprocessing, target2
    // Extract key-value pairs from the Condition field
    UNWIND conditions AS condition
    WITH row2, condition, subprocess2, target2, preprocessing
    WHERE condition CONTAINS '='
    WITH row2, subprocess2,target2, preprocessing, trim(SPLIT(condition, '=')[0]) AS key, trim(SPLIT(condition, '=')[1]) AS value
    WITH row2, subprocess2,target2, preprocessing, key, SPLIT(value, ' ')[0] AS number, SPLIT(value, ' ')[1] AS unit, value
    WITH row2, subprocess2, target2, preprocessing ,key, value, number, unit,    
        CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN apoc.number.parseFloat(number) ELSE value END AS parsed_value,
        CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN unit ELSE NULL END AS parsed_unit
    // Use APOC to dynamically create Parameter nodes and set properties
    // Check if the value part is a number and create the appropriate node and relationships
    CALL apoc.do.when(
    subprocess2.isNew IS NOT NULL,
    '
    // Create the Parameter node
    MATCH (sp)
    WHERE id(sp) = $subprocess2Id
    CREATE(param:Parameter {{uid: RandomUUID()}}    
    // Conditionally set the key-value property if the value is numeric
    FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN [1] ELSE [] END |
        SET param.name = key,param.value = number,param.unit = unit
    
    )
    
    // Conditionally set the key-value property if the value is not numeric
    FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NULL THEN [1] ELSE [] END |
        SET param.Technique = key, param.Value = value 
    )
    MERGE (subprocess2)-[:HAS_PARAMETER]->(param)
    ',
  '',
  {{
    subprocess2Id: id(subprocess2),
    key: key,
    value: value
  }}
) YIELD value AS thing
    
    WITH row2, preprocessing, subprocess2, target2
    ORDER BY toInteger(row2.Step)
    
    // Match the next step and check if the target of the current step is used as a precursor in the next step
    MATCH (next_row2  {{ExperimentID: row2.ExperimentID, step: toInteger(row2.Step) + 1}})
    WITH row2, preprocessing, subprocess2, target2, next_row2
    
    // Compare target and precursor names
    WHERE target2.name = next_row2.Precursor
    MERGE (target2)-[:IS_DATAPROCESSING_INPUT]->(subprocess2);
    """,
    f'''    
    // Step 6: Image Analysis
    LOAD CSV WITH HEADERS FROM 'file:///schema_ingestion/temp/anal.csv' AS row2 FIELDTERMINATOR ';'
WITH row2,SPLIT(row2.Condition, "
") AS conditions,SPLIT(row2.Software, "
") AS softwares,SPLIT(row2.AmountPrecursor, ' ') AS precursorAmountParts, SPLIT(row2.AmountTarget, ' ') AS targetAmountParts

ORDER BY toInteger(row2.Step) // Ensure rows are processed in order of steps

MERGE (test_exp:Experiment  {{identifier:row2.ExperimentID }})
MERGE (preprocessing:DataProcessing:Process {{name:"DataAnalysis", identifier:row2.ExperimentID}})
ON CREATE SET preprocessing.uid = RandomUUID()
MERGE (test_exp)-[:HAS_PROCESS]->(preprocessing)
// Create or merge nodes for subprocess, component, target, and condition
MERGE (subprocess2:DataProcessing:Process  {{name: row2.Technique, identifier: row2.ExperimentID, step: toInteger(row2.Step)}})
ON CREATE SET
subprocess2.uid = RandomUUID(),
subprocess2.isNew = true
MERGE (component2:Data  {{name: row2.Precursor, identifier: row2.ExperimentID}})-[:HAS_PROPERTY]->(component2amount:Property {{name: 'amount'}})

ON CREATE SET
component2amount.value = apoc.number.parseFloat(precursorAmountParts[0]),
component2amount.unit = CASE WHEN size(precursorAmountParts) > 1 THEN precursorAmountParts[1] ELSE NULL END
MERGE (target2:Property  {{name: row2.Target, identifier: row2.ExperimentID}})

ON CREATE SET
target2.value = apoc.number.parseFloat(targetAmountParts[0]),
target2.unit = CASE WHEN size(targetAmountParts) > 1 THEN targetAmountParts[1] ELSE NULL END

MERGE (preprocessing)-[:HAS_PART]->(subprocess2)
MERGE (component2)-[:IS_DATAPROCESSING_INPUT]->(subprocess2)
MERGE (subprocess2)-[:YIELDS_PROPERTY]->(target2)

WITH row2, preprocessing, subprocess2, target2, softwares, conditions
UNWIND softwares AS software
WITH row2, subprocess2, target2, preprocessing, software, conditions
WHERE software CONTAINS '='
WITH row2, subprocess2, target2, preprocessing, trim(SPLIT(software, '=')[0]) AS key, trim(SPLIT(software, '=')[1]) AS value, conditions
// Carry forward data for comparison in the next step
CALL apoc.do.when(
subprocess2.isNew IS NOT NULL,
'
// Create the Parameter node
CREATE (soft:Metadata {{uid: randomUUID()}})
WITH soft, $key AS key, $value AS value, $subprocess2 AS subprocess2, $conditions AS conditions,
     $preprocessing AS preprocessing, $row2 AS row2, $target2 AS target2
     

// Set properties on the Parameter node
CALL apoc.create.setProperties(soft, [key], [value]) YIELD node AS updated_soft
SET updated_soft.name = updated_soft.Software
REMOVE updated_soft.Software
// Create the relationship
MERGE (subprocess2)-[:HAS_PARAMETER]->(updated_soft)

// Continue with the rest of your query


RETURN true as continue
',
'
RETURN true as continue
',
{{
    key: key,
value:value,
subprocess2:subprocess2,
conditions:conditions,
preprocessing:preprocessing,
row2:row2,
target2:target2
}}
)
YIELD value AS stuff

WITH *, [c IN conditions WHERE c CONTAINS "="] AS filteredConditions
WITH *
CALL apoc.do.when(
size(filteredConditions) > 0 AND subprocess2.isNew IS NOT NULL,
'
UNWIND filteredConditions AS condition

WITH row2, subprocess2, target2, preprocessing,
   trim(SPLIT(condition, "=")[0]) AS key,
   trim(SPLIT(condition, "=")[1]) AS value

WITH row2, subprocess2, target2, preprocessing, key,
   SPLIT(value, " ")[0] AS number,
   SPLIT(value, " ")[1] AS unit, value

WITH row2, subprocess2, target2, preprocessing, key, value, number, unit,
   CASE
     WHEN apoc.number.parseFloat(number) IS NOT NULL THEN apoc.number.parseFloat(number)
     ELSE value
   END AS parsed_value,
   CASE
     WHEN apoc.number.parseFloat(number) IS NOT NULL THEN unit
     ELSE NULL
   END AS parsed_unit

// Create the Parameter node
CREATE (param:Parameter {{uid: randomUUID()}})

// Conditionally set the key-value property if the value is numeric
FOREACH (_ IN CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN [1] ELSE [] END |
SET param.name = key, param.value = parsed_value, param.unit = parsed_unit
)

// Conditionally set the key-value property if the value is not numeric
FOREACH (_ IN CASE WHEN apoc.number.parseFloat(number) IS NULL THEN [1] ELSE [] END |
SET param.name = key, param.value = value
)

// Create the relationship
MERGE (subprocess2)-[:HAS_PARAMETER]->(param)

RETURN true AS continue
',
'
RETURN true as continue
',
{{
    key: key,
value:value,
subprocess2:subprocess2,
conditions:conditions,
preprocessing:preprocessing,
row2:row2,
target2:target2
}}
)
YIELD value as result
REMOVE subprocess2.isNew
WITH *
// Carry forward data for comparison in the next step
WITH *
ORDER BY toInteger(row2.Step)

WITH *

// Match the next step and check if the target of the current step is used as a precursor in the next step
MATCH (next_row2  {{identifier: row2.ExperimentID, step: toInteger(row2.Step) + 1}})
WITH *

// Compare target and precursor names
WHERE target2.name = next_row2.Precursor
MERGE (target2)-[:IS_DATAPROCESSING_INPUT]->(subprocess2)

      ''']
    # Add BASE_DIR to the file path

def ingest_data(file_path):
    file_path = os.path.join('schema_ingestion', 'temp')
    queries = get_query(file_path)
    for query in queries:
        print(query)
        db.cypher_query(query)
