MERGE (vb:Material {
name: "VULCAN XC72",
date_added: date()
})
ON CREATE
SET vb.uid = randomUUID()
MERGE (cb:Material {
  name: "Carbon Black",
  date_added: date()
})
ON CREATE
SET cb.uid = randomUUID()

WITH cb, vb
MATCH(c:Element {symbol: "C"})
MATCH(emmo_cb:EMMOMatter {name: "CarbonBlack"})
MERGE(vb)-[:IS_A]->(emmo_cb)
MERGE(cb)-[:IS_A]->(emmo_cb)
MERGE(vb)-[:HAS_PART]->(c)
MERGE(cb)-[:HAS_PART]->(c);

LOAD CSV WITH HEADERS FROM 'file:///home/mdreger/Documents/data/neo4j_data/materials/Catalysts.csv' AS row
MATCH (ontology:EMMOMatter {name:row.Ontology})
MERGE(cat:Material{name: row.Name,
                   chemical_formula: row.ChemicalFormula
})
  ON CREATE
  SET cat.uid = randomUUID()
MERGE(cat)-[:IS_A]->(ontology)
SET cat.name = row.Name,  cat.CAS = row.CAS


WITH row, cat
MATCH(cat:Material{name: row.Name, chemical_formula: row.ChemicalFormula})
MATCH (part1:Material {symbol:row.HasPart1})
MERGE(cat)-[:HAS_PART]->(part1)

WITH row, cat
MATCH(cat:Material{name: row.Name, chemical_formula: row.ChemicalFormula})
MATCH (part2:Material {name:row.HasPart2})
MERGE(cat)-[:HAS_PART]->(part2)


WITH row, cat
MATCH(cat:Material{name: row.Name, chemical_formula: row.ChemicalFormula})
MATCH (part3:Material {symbol:row.HasPart3})
MERGE(cat)-[:HAS_PART]->(part3)

WITH row, cat
MATCH (part3:Material {symbol:row.HasPart3})
MERGE(test)-[:HAS_PART]->(part3);

LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/MaxDreger92/MatGraphAI/master/mat2devplatform/matgraph/data/materials/Catalysts.csv' AS row
MATCH(cat:Material{name: row.Name, chemical_formula: row.ChemicalFormula})
MATCH(emmo_purity:EMMOQuantity{name: "MetalPurity"})
FOREACH(x IN CASE WHEN row.Purity IS NOT NULL THEN [1] END |
MERGE (purity:Property {name:row.Name+ "_purity"})
MERGE(purity)-[:IS_A]->(emmo_purity)
ON CREATE
SET purity.uid = randomUUID()
MERGE(cat)-[:HAS_PROPERTY {float_value: toFloat(row.Purity)}]->(purity)
)

WITH row, cat
MATCH (emmo_ratio:EMMOQuantity {name: "CatalystIonomerRatio"})
MERGE (ratio:Property {name:row.Name+ "_ratio"})
MERGE(ratio)-[:IS_A]->(emmo_ratio)
MERGE(cat)-[:HAS_PROPERTY {float_value: toFloat(row.CatalystIonomerRatio)}]->(ratio)
