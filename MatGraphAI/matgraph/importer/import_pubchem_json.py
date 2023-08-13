IMPORT_PUBCHEM = '''
WITH '$data' AS data
WITH apoc.convert.fromJsonList(data) AS rows
UNWIND rows as row

MATCH (mw:EMMOQuantity {name: "MolecularWeight"}),
(c:Element {symbol: "C"}),
(h:Element {symbol: "H"}),
(o:Element {symbol: "O"}),
(n:Element {symbol: "N"}),
(f:Element {symbol: "F"}),
(s:Element {symbol: "S"}),
(label1:EMMOMatter {name: row.ontologylabel1})

MERGE(solvent:Molecule {name: row.cmpdname,
SMILES : row.isosmiles,
InChi_Key : row.inchikey,
IUPAC_name : row.iupacname,
InChi: row.inchi,
chemical_formula: row.mf})
ON CREATE
SET solvent.uid = randomUUID()

FOREACH(x IN CASE WHEN row.C <> "" THEN [1] END |
MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.C)}]->(c))

FOREACH(x IN CASE WHEN row.H <> "" THEN [1] END |
MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.H)}]->(h))

FOREACH(x IN CASE WHEN row.O <> "" THEN [1] END |
MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.O)}]->(o))

FOREACH(x IN CASE WHEN row.N <> "" THEN [1] END |
MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.N)}]->(n))

FOREACH(x IN CASE WHEN row.F <> "" THEN [1] END |
MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.F)}]->(f))

FOREACH(x IN CASE WHEN row.S <> "" THEN [1] END |
MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.S)}]->(s))

FOREACH(x IN CASE WHEN row.ontologylabel1 = label1.name THEN [1] END |
MERGE (solvent)-[:IS_A]->(label1))

//FOREACH(x IN CASE WHEN row.ontologylabel1 <> "" THEN [1] END |
// MERGE (solvent)-[:IS_A ]->(:Resource:EMMOMatter:EMMO__Class {name: row.ontologylabel1}))

FOREACH(x IN CASE WHEN toFloat(row.mw) <> "" THEN [1] END |
MERGE(pmw:Property{uid: randomUUID(),
date_added : '1111-11-11'
})
MERGE (solvent)-[:HAS_PROPERTY {value: toFloat(row.mw)}]->(pmw)-[:IS_A]->(mw))
'''


IMPORT_RESEARCHER = '''
WITH '$data' AS data
WITH apoc.convert.fromJsonList(data) AS rows
UNWIND rows as row

MERGE (researcher:Researcher{
  ORCID: row.`ORCID`,
  last_name: row.`last_name`,
  first_name: row.first_name,
  date_of_birth: row.date_of_birth,
  date_added: row.date_added,
  field: row.field,
  academic_title: row.title,
  uid: randomUUID(),
  name: row. first_name + " " + row.last_name
})
WITH researcher, row
MATCH(country:Country {name: row.`country`})
MATCH(institution:Institution {name: row.`institution`})


MERGE(researcher)-[:IN]->(country)
MERGE(researcher)-[:AFFILIATED_TO]->(institution)

'''