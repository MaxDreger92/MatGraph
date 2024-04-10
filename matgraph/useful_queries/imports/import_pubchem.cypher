// Molecule import starts here

LOAD CSV WITH HEADERS FROM 'file:///home/mdreger/Documents/data/neo4j_data/materials/PubChemMolecules_sum.csv' AS row

MATCH (mw:EMMOQuantity {name: "MolecularWeight"}),
      (c:Element {symbol: "C"}),
      (h:Element {symbol: "H"}),
      (o:Element {symbol: "O"}),
      (n:Element {symbol: "N"}),
      (f:Element {symbol: "F"}),
      (s:Element {symbol: "S"}),
      (label1:EMMOMatter {name: row.ontologylabel1}),
      (label2:EMMOMatter {name: row.ontologylabel1})




MERGE(solvent:Molecule {name: row.cmpdname,
                         SMILES : row.isosmiles,
                         InChi_Key : row.inchikey,
                         IUPAC_name : row.iupacname,
                         InChi: row.inchi,
                         chemical_formula: row.mf})
ON CREATE
SET solvent.uid = randomUUID()


FOREACH(x IN CASE WHEN row.C IS NOT NULL THEN [1] END |
  MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.C)}]->(c))

FOREACH(x IN CASE WHEN row.H IS NOT NULL THEN [1] END |
  MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.H)}]->(h))

FOREACH(x IN CASE WHEN row.O IS NOT NULL THEN [1] END |
  MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.O)}]->(o))

FOREACH(x IN CASE WHEN row.N IS NOT NULL THEN [1] END |
  MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.N)}]->(n))

FOREACH(x IN CASE WHEN row.F IS NOT NULL THEN [1] END |
  MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.F)}]->(f))

FOREACH(x IN CASE WHEN row.S IS NOT NULL THEN [1] END |
  MERGE (solvent)-[:HAS_PART {integer_value: toInteger(row.S)}]->(s))

FOREACH(x IN CASE WHEN row.ontologylabel1 = label1.name THEN [1] END |
  MERGE (solvent)-[:IS_A ]->(label1))

//FOREACH(x IN CASE WHEN row.ontologylabel1 IS NOT NULL THEN [1] END |
//  MERGE (solvent)-[:IS_A ]->(:Resource:EMMOMatter:EMMO__Class {name: row.ontologylabel1}))

FOREACH(x IN CASE WHEN toFloat(row.mw) IS NOT NULL THEN [1] END |
  MERGE(pmw:Property{uid: randomUUID(),
                          date_added : '1111-11-11'
  })
  MERGE (solvent)-[:HAS_PROPERTY {value: toFloat(row.mw)}]->(pmw)-[:IS_A]->(mw));


