// Step 1: Load the initial CSV and create nodes
LOAD CSV WITH HEADERS FROM 'file:///org.csv' AS row FIELDTERMINATOR ';'
WITH row, SPLIT(row.Author,'\n') AS authors, SPLIT(row.ORCID,'\n') AS orcids, SPLIT(row.Email,'\n') AS emails

MERGE (HIP:FoundingBody {name:row.FoundingBody, grant_number:546546})
CREATE (test_exp:Experiment {title:row.ExperimentTitle, pida:row.ExperimentID, date_added:row.UploadDate })
MERGE (test_exp) -[:HAS_FOUNDER]-> (HIP)
MERGE (ForschungszentrumJuelich:Institution {name:row.Institution, center_id:555, acronym:'FZJ',wikipedia_link:'link', center_type:'Research Centre'})
MERGE (test_exp)-[:PUBLISHED_BY]->(ForschungszentrumJuelich)
MERGE (Germany:Country{name:row.Country})
MERGE (ForschungszentrumJuelich)-[:IN]->(Germany)
MERGE (RSC:Publication {title:row.Publication, published:row.Published, doi:row.DOI, journal:row.Journal,volume: row.Volume, issue: row.Issue, pages: row.Pages, publishing_date: row.PublicationDate})
MERGE (test_exp)-[:PUBLISHED_IN]->(RSC)

CREATE (tags_exp:Tags{topic: row.Topic, device:row.Device, component: row.Component, granularity:row.Granularity})
MERGE (test_exp)-[:TAGGED_AS]->(tags_exp)
MERGE (exp_pics:File {name:row.FileName, format:row.Format, link:row.Link, file_size:row.FileSize, dimension_x:row.DimensionX, dimension_y:row.DimensionY, dimension_z:row.DimensionZ, px_per_metric: row.PixelPerMetric, mask_exist:row.MaskExist, mask_link:row.MaskLink})
CREATE (test_exp)-[:HAS]->(exp_pics)
CREATE (sample_preparation_process:Manufacturing {name: 'SamplePreparation', exp_id:row.ExperimentID})
CREATE (test_exp)-[:HAS_PROCESS]->(sample_preparation_process)
CREATE (synthesis_process:Manufacturing {name: 'Synthesis', exp_id:row.ExperimentID})
MERGE (test_exp)-[:HAS_PROCESS]->(synthesis_process)

WITH row,test_exp, RSC, authors, orcids, emails, sample_preparation_process
// Loop over the authors and orcids lists
UNWIND range(0, size(authors) - 1) AS idx
WITH row,test_exp, RSC, authors[idx] AS author, orcids[idx] AS orcid, emails[idx] AS email, sample_preparation_process
// Create or merge the Author nodes with corresponding ORCID properties
MERGE (a:Author {name: author})
ON CREATE SET a.orcid = orcid
ON CREATE SET a.email = email
MERGE (a)-[:IS_AUTHOR]->(RSC)
MERGE (a)-[:CONDUCTED]->(test_exp)

WITH test_exp, sample_preparation_process

// Step 2: Load the second CSV and create nodes
LOAD CSV WITH HEADERS FROM 'file:///sp.csv' AS row1 FIELDTERMINATOR ';'
WITH row1, sample_preparation_process, SPLIT(row1.Condition, '\n') AS conditions,SPLIT(row1.AmountPrecursor, ' ') AS precursorAmountParts, SPLIT(row1.AmountTarget, ' ') AS targetAmountParts

ORDER BY toInteger(row1.Step) // Ensure rows are processed in order of steps

// Create or merge nodes for subprocess, component, target, and condition
MERGE (subprocess1:Manufacturing {name: row1.Technique, exp_id: row1.ExperimentID, step: toInteger(row1.Step)})
MERGE (component1:Matter {name: row1.Precursor, exp_id: row1.ExperimentID})
ON CREATE SET
    component1.Amount = apoc.number.parseFloat(precursorAmountParts[0]),
    component1.Unit = CASE WHEN size(precursorAmountParts) > 1 THEN precursorAmountParts[1] ELSE NULL END
MERGE (target1:Matter {name: row1.Target, exp_id: row1.ExperimentID})
ON CREATE SET
    target1.amount = apoc.number.parseFloat(targetAmountParts[0]),
    target1.unit = CASE WHEN size(targetAmountParts) > 1 THEN targetAmountParts[1] ELSE NULL END

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

// Create the Parameter node
CALL apoc.create.node(['Parameter'], {}) YIELD node AS param

// Conditionally set the key-value property if the value is numeric
FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN [1] ELSE [] END |
    SET param.Parameter = key,param.Value = number,param.Unit = unit

)

// Conditionally set the key-value property if the value is not numeric
FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NULL THEN [1] ELSE [] END |
    SET param.Parameter = key, param.Value = value
)

MERGE (subprocess1)-[:HAS_PARAMETER]->(param)

// Carry forward data for comparison in the next step
WITH row1, subprocess1, target1
ORDER BY toInteger(row1.Step)

// Match the next step and check if the target of the current step is used as a precursor in the next step
MATCH (next_row1 {ExperimentID: row1.ExperimentID, Step: toInteger(row1.Step) + 1})
WITH row1, subprocess1, target1, next_row1

// Compare target and precursor names
WHERE target1.name = next_row1.Precursor
MERGE (target1)-[:IS_MANUFACTURING_INPUT]->(subprocess1);

// Step 3: Ensure the synthesis_process node exists
// Load the third CSV file
LOAD CSV WITH HEADERS FROM 'file:///syn.csv' AS row2 FIELDTERMINATOR ';'
WITH row2, SPLIT(row2.Condition, '\n') AS conditions,SPLIT(row2.AmountPrecursor, ' ') AS precursorAmountParts, SPLIT(row2.AmountTarget, ' ') AS targetAmountParts
ORDER BY toInteger(row2.Step) // Ensure rows are processed in order of steps

// Create or merge nodes for subprocess, component, target, and condition
MERGE (synthesis_process:Manufacturing {name: 'Synthesis', exp_id:row2.ExperimentID})
MERGE (subprocess2:Manufacturing {name: row2.Technique, exp_id: row2.ExperimentID, step: toInteger(row2.Step)})
MERGE (component2:Matter {name: row2.Precursor, exp_id: row2.ExperimentID})
ON CREATE SET
    component2.Amount = apoc.number.parseFloat(precursorAmountParts[0]),
    component2.Unit = CASE WHEN size(precursorAmountParts) > 1 THEN precursorAmountParts[1] ELSE NULL END
MERGE (target2:Matter {name: row2.Target, exp_id: row2.ExperimentID})
ON CREATE SET
    target2.amount = apoc.number.parseFloat(targetAmountParts[0]),
    target2.unit = CASE WHEN size(targetAmountParts) > 1 THEN targetAmountParts[1] ELSE NULL END

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
CALL apoc.create.node(['Parameter'], {}) YIELD node AS param

// Conditionally set the key-value property if the value is numeric
FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN [1] ELSE [] END |
    SET param.Parameter = key,param.Value = number,param.Unit = unit

)

// Conditionally set the key-value property if the value is not numeric
FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NULL THEN [1] ELSE [] END |
    SET param.Parameter = key, param.Value = value
)

MERGE (subprocess2)-[:HAS_PARAMETER]->(param)

// Carry forward data for comparison in the next step
WITH row2, synthesis_process, subprocess2, target2
ORDER BY toInteger(row2.Step)

// Match the next step and check if the target of the current step is used as a precursor in the next step
MATCH (next_row2 {ExperimentID: row2.ExperimentID, Step: toInteger(row2.Step) + 1})
WITH row2, synthesis_process, subprocess2, target2, next_row2

// Compare target and precursor names
WHERE target2.name = next_row2.Precursor
MERGE (target2)-[:IS_MANUFACTURING_INPUT]->(subprocess2);

//Step4: Loading Characterization Method

// Load the fourth CSV file
LOAD CSV WITH HEADERS FROM 'file:///char.csv' AS row3 FIELDTERMINATOR ';'
WITH row3
ORDER BY toInteger(row3.Step) // Ensure rows are processed in order of steps
MERGE (test_exp:Experiment {pida:row3.ExperimentID })
CREATE (characterization:Measurement{method:row3.MeasurementMethod,measurement_type:row3.MeasurementType, specimen:row3.Specimen, exp_id:row3.ExperimentID})
CREATE (test_exp)-[:HAS_PROCESS]->(characterization)
MERGE (Sample:Matter{name:'Sample',exp_id:row3.ExperimentID})
CREATE (Sample)-[:IS_MEASUREMENT_INPUT]->(characterization)
CREATE (temperature2:Parameter{name:'Temperature',Temperature:row3.Temperature, Unit:row3.TemperatureUnit})
CREATE (humidity:Parameter{name:'Humidity', Humidity:row3.Humidity, Unit:row3.HumidityUnit})
CREATE (atmosphere:Parameter{name:'Atmosphere', Atmosphere:row3.Atmosphere, Unit:row3.AtmosphereUnit})
CREATE (pressure:Parameter{name:'Pressure',Pressure:row3.Pressure, Unit:row3.PressureUnit})
CREATE (characterization)-[:HAS_PARAMETER]->(temperature2)
CREATE (characterization)-[:HAS_PARAMETER]->(humidity)
CREATE (characterization)-[:HAS_PARAMETER]->(atmosphere)
CREATE (characterization)-[:HAS_PARAMETER]->(pressure)

CREATE (calibration:Parameter{name:'Calibration',steps:row3.Calibration})
CREATE (characterization)-[:HAS_PARAMETER]->(calibration)
CREATE (raw_data:Data{name:'RawData',exp_id:row3.ExperimentID,link:'link'})
CREATE (characterization)-[:HAS_MEASUREMENT_OUTPUT]->(raw_data);

// Load the instrument and measurement details
LOAD CSV WITH HEADERS FROM 'file:///inst.csv' AS row FIELDTERMINATOR ';'
CALL apoc.create.node(['Instrument'], apoc.map.fromPairs([key IN keys(row) | [key, row[key]]])) YIELD node
MERGE (characterization:Measurement {exp_id:row.ExperimentID})
MERGE (instrument:Instrument{ExperimentID:row.ExperimentID})
MERGE (characterization)-[:BY_INSTRUMENT]->(instrument);

// Step 5: Image preprocessing
// Load the fifth CSV file
LOAD CSV WITH HEADERS FROM 'file:///pre.csv' AS row2 FIELDTERMINATOR ';'
WITH row2,SPLIT(row2.Condition, '\n') AS conditions, SPLIT(row2.Software, '\n') AS softwares,SPLIT(row2.AmountPrecursor, ' ') AS precursorAmountParts, SPLIT(row2.AmountTarget, ' ') AS targetAmountParts
ORDER BY toInteger(row2.Step) // Ensure rows are processed in order of steps

MERGE (test_exp:Experiment {pida:row2.ExperimentID })
MERGE (preprocessing:DataProcessing{name:"DataPreprocessing", exp_id:row2.ExperimentID})
MERGE (test_exp)-[:HAS_PROCESS]->(preprocessing)
// Create or merge nodes for subprocess, component, target, and condition
MERGE (subprocess2:DataProcessing {name: row2.Technique, exp_id: row2.ExperimentID, step: toInteger(row2.Step)})
MERGE (component2:Data {name: row2.Precursor, exp_id: row2.ExperimentID})
ON CREATE SET
    component2.Amount = apoc.number.parseFloat(precursorAmountParts[0]),
    component2.Unit = CASE WHEN size(precursorAmountParts) > 1 THEN precursorAmountParts[1] ELSE NULL END
MERGE (target2:Data {name: row2.Target, exp_id: row2.ExperimentID})
ON CREATE SET
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
CALL apoc.create.node(['Parameter'], {}) YIELD node AS soft
CALL apoc.create.setProperties(soft, [key], [value]) YIELD node AS updated_soft
MERGE (subprocess2)-[:HAS_PARAMETER]->(updated_soft)

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

// Create the Parameter node
CALL apoc.create.node(['Parameter'], {}) YIELD node AS param

// Conditionally set the key-value property if the value is numeric
FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN [1] ELSE [] END |
    SET param.Technique = key,param.Value = number,param.Unit = unit

)

// Conditionally set the key-value property if the value is not numeric
FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NULL THEN [1] ELSE [] END |
    SET param.Technique = key, param.Value = value
)
MERGE (subprocess2)-[:HAS_PARAMETER]->(param)


WITH row2, preprocessing, subprocess2, target2
ORDER BY toInteger(row2.Step)

// Match the next step and check if the target of the current step is used as a precursor in the next step
MATCH (next_row2 {ExperimentID: row2.ExperimentID, Step: toInteger(row2.Step) + 1})
WITH row2, preprocessing, subprocess2, target2, next_row2

// Compare target and precursor names
WHERE target2.name = next_row2.Precursor
MERGE (target2)-[:IS_DATAPROCESSING_INPUT]->(subprocess2);

// Step 6: Image Analysis
// Load the fifth CSV file
LOAD CSV WITH HEADERS FROM 'file:///anal.csv' AS row2 FIELDTERMINATOR ';'
WITH row2,SPLIT(row2.Condition, '\n') AS conditions,SPLIT(row2.Software, '\n') AS softwares,SPLIT(row2.AmountPrecursor, ' ') AS precursorAmountParts, SPLIT(row2.AmountTarget, ' ') AS targetAmountParts

ORDER BY toInteger(row2.Step) // Ensure rows are processed in order of steps

MERGE (test_exp:Experiment {pida:row2.ExperimentID })
MERGE (preprocessing:DataProcessing{name:"DataAnalysis", exp_id:row2.ExperimentID})
MERGE (test_exp)-[:HAS_PROCESS]->(preprocessing)
// Create or merge nodes for subprocess, component, target, and condition
MERGE (subprocess2:DataProcessing {name: row2.Technique, exp_id: row2.ExperimentID, step: toInteger(row2.Step)})
MERGE (component2:Data {name: row2.Precursor, exp_id: row2.ExperimentID})
ON CREATE SET
    component2.Amount = apoc.number.parseFloat(precursorAmountParts[0]),
    component2.Unit = CASE WHEN size(precursorAmountParts) > 1 THEN precursorAmountParts[1] ELSE NULL END
MERGE (target2:Data {name: row2.Target, exp_id: row2.ExperimentID})
ON CREATE SET
    target2.amount = apoc.number.parseFloat(targetAmountParts[0]),
    target2.unit = CASE WHEN size(targetAmountParts) > 1 THEN targetAmountParts[1] ELSE NULL END

MERGE (preprocessing)-[:HAS_PART]->(subprocess2)
MERGE (component2)-[:IS_DATAPROCESSING_INPUT]->(subprocess2)
MERGE (subprocess2)-[:YIELDS_PROPERTY]->(target2)

WITH row2, preprocessing, subprocess2, target2, softwares, conditions
UNWIND softwares AS software
WITH row2, subprocess2, target2, preprocessing, software, conditions
WHERE software CONTAINS '='
WITH row2, subprocess2,target2, preprocessing, trim(SPLIT(software, '=')[0]) AS key, trim(SPLIT(software, '=')[1]) AS value, conditions
// Carry forward data for comparison in the next step
CALL apoc.create.node(['Parameter'], {}) YIELD node AS soft
CALL apoc.create.setProperties(soft, [key], [value]) YIELD node AS updated_soft
MERGE (subprocess2)-[:HAS_PARAMETER]->(updated_soft)

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

// Create the Parameter node
CALL apoc.create.node(['Parameter'], {}) YIELD node AS param

// Conditionally set the key-value property if the value is numeric
FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN [1] ELSE [] END |
    SET param.Technique = key,param.Value = number,param.Unit = unit

)

// Conditionally set the key-value property if the value is not numeric
FOREACH (ignore IN CASE WHEN apoc.number.parseFloat(number) IS NULL THEN [1] ELSE [] END |
    SET param.Technique = key, param.Value = value
)
MERGE (subprocess2)-[:HAS_PARAMETER]->(param)

// Carry forward data for comparison in the next step
WITH row2, preprocessing, subprocess2, target2
ORDER BY toInteger(row2.Step)

// Match the next step and check if the target of the current step is used as a precursor in the next step
MATCH (next_row2 {ExperimentID: row2.ExperimentID, Step: toInteger(row2.Step) + 1})
WITH row2, preprocessing, subprocess2, target2, next_row2

// Compare target and precursor names
WHERE target2.name = next_row2.Precursor
MERGE (target2)-[:IS_DATAPROCESSING_INPUT]->(subprocess2);



LOAD CSV WITH HEADERS FROM 'file:///schema_ingestion/temp/anal.csv' AS row2 FIELDTERMINATOR ';'
WITH row2,SPLIT(row2.Condition, "
") AS conditions,SPLIT(row2.Software, "
") AS softwares,SPLIT(row2.AmountPrecursor, ' ') AS precursorAmountParts, SPLIT(row2.AmountTarget, ' ') AS targetAmountParts

ORDER BY toInteger(row2.Step) // Ensure rows are processed in order of steps

MERGE (test_exp:Experiment  {pida:row2.ExperimentID })
MERGE (preprocessing:DataProcessing {name:"DataAnalysis", exp_id:row2.ExperimentID})
MERGE (test_exp)-[:HAS_PROCESS]->(preprocessing)
// Create or merge nodes for subprocess, component, target, and condition
MERGE (subprocess2:DataProcessing  {name: row2.Technique, exp_id: row2.ExperimentID, step: toInteger(row2.Step)})
ON CREATE SET
subprocess2.uid = RandomUUID(),
subprocess2.isNew = true
MERGE (component2:Data  {name: row2.Precursor, exp_id: row2.ExperimentID})
ON CREATE SET
component2.Amount = apoc.number.parseFloat(precursorAmountParts[0]),
component2.Unit = CASE WHEN size(precursorAmountParts) > 1 THEN precursorAmountParts[1] ELSE NULL END
MERGE (target2:Data  {name: row2.Target, exp_id: row2.ExperimentID})
ON CREATE SET
target2.amount = apoc.number.parseFloat(targetAmountParts[0]),
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
CREATE (soft:Parameter {uid: randomUUID()})
WITH soft, $key AS key, $value AS value, $subprocess2 AS subprocess2, $conditions AS conditions,
     $preprocessing AS preprocessing, $row2 AS row2, $target2 AS target2

// Set properties on the Parameter node
CALL apoc.create.setProperties(soft, [key], [value]) YIELD node AS updated_soft

// Create the relationship
MERGE (subprocess2)-[:HAS_PARAMETER]->(updated_soft)

// Continue with the rest of your query


RETURN true as continue
',
'
RETURN true as continue
',
{
key: key,
value:value,
subprocess2:subprocess2,
conditions:conditions,
preprocessing:preprocessing,
row2:row2,
target2:target2
}
)
YIELD value AS stuff

WITH *, [c IN conditions WHERE c CONTAINS "="] AS filteredConditions
CREATE (:testoe)
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
CREATE (param:Parameter {uid: randomUUID()})

// Conditionally set the key-value property if the value is numeric
FOREACH (_ IN CASE WHEN apoc.number.parseFloat(number) IS NOT NULL THEN [1] ELSE [] END |
SET param.name = key, param.value = parsed_value, param.unit = parsed_unit
)

// Conditionally set the key-value property if the value is not numeric
FOREACH (_ IN CASE WHEN apoc.number.parseFloat(number) IS NULL THEN [1] ELSE [] END |
SET param.Technique = key, param.Value = value
)

// Create the relationship
MERGE (subprocess2)-[:HAS_PARAMETER]->(param)

RETURN true AS continue
',
'
RETURN true as continue
',
{
key: key,
value:value,
subprocess2:subprocess2,
conditions:conditions,
preprocessing:preprocessing,
row2:row2,
target2:target2
}
)
YIELD value as result
REMOVE subprocess2.isNEw
WITH *
// Carry forward data for comparison in the next step
WITH *
ORDER BY toInteger(row2.Step)

WITH *

// Match the next step and check if the target of the current step is used as a precursor in the next step
MATCH (next_row2  {ExperimentID: row2.ExperimentID, Step: toInteger(row2.Step) + 1})
WITH *

// Compare target and precursor names
WHERE target2.name = next_row2.Precursor
MERGE (target2)-[:IS_DATAPROCESSING_INPUT]->(subprocess2)



