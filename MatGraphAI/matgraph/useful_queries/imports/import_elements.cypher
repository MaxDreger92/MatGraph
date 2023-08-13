LOAD CSV WITH HEADERS FROM 'file:///home/mdreger/Documents/data/neo4j_data/materials/elements.csv' AS line

MATCH(atomicnumber:EMMOQuantity {name: "AtomicNumber"}),
     (atomicmass:EMMOQuantity {name: "AtomicMass"}),
     (molarheat:EMMOQuantity {name: "MolarHeat"}),
     (elementalsubstance:EMMOMatter {name: "ElementalSubstance"}),
     (density:EMMOQuantity {name: "Density"}),
     (melt:EMMOQuantity {name: "MeltingPoint"}),
     (electronegativity:EMMOQuantity {name: "ElectronegativityPauling"}),
     (electronaffinity:EMMOQuantity {name: "ElectronAffinity"}),
     (ionizationenergy:EMMOQuantity {name: "IonizationEnergy"})



// Create Nodes
CREATE (el:Element {name: line.name, summary: line.name, symbol : line.symbol, uid: randomUUID()})
MERGE (el)-[:IS_A]->(elementalsubstance)

FOREACH(x IN CASE WHEN line.discovered_by IS NOT NULL THEN [1] END |
  MERGE (researcher:Researcher {name: line.discovered_by})
    ON CREATE SET
    researcher.uid = randomUUID(),
    researcher.date_added = date()
  CREATE (exp:Manufacturing {uid: randomUUID()})
  MERGE (el)<-[:IS_MANUFACTURING_OUTPUT]-(exp)-[:BY]->(researcher))
// IntegerProperties

CREATE (el)-[:HAS_PROPERTY {integer_value : toInteger(line.number)}]->(atomicnumber)

//FloatProperties
FOREACH(x IN CASE WHEN NOT NULL in line.`ionization_energies` THEN [1] END |
  MERGE(pionizationenergy:Property{uid: randomUUID(),
                          date_added : date()
  })
  MERGE (el)-[:HAS_PROPERTY {list_value: apoc.convert.fromJsonList(line.`ionization_energies`)}]
  ->(pionizationenergy)-[:IS_A]->(ionizationenergy))

FOREACH(x IN CASE WHEN line.electron_affinity IS NOT NULL THEN [1] END |
  MERGE(pelaff:Property{uid: randomUUID(),
                                   date_added : date()
  })
  MERGE (el)-[:HAS_PROPERTY {float_value: toFloat(line.electron_affinity)}]->(pelaff)-[:IS_A]->(electronaffinity))

FOREACH(x IN CASE WHEN line.electronegativity_pauling IS NOT NULL THEN [1] END |
  MERGE(pelneg:Property{uid: randomUUID(),
                                   date_added : date()
  })
  MERGE (el)-[:HAS_PROPERTY {float_value: toFloat(line.electronegativity_pauling)}]->(pelneg)-[:IS_A]->(electronegativity))

FOREACH(x IN CASE WHEN line.melt IS NOT NULL THEN [1] END |
  MERGE(pmelt:Property{uid: randomUUID(),
                                   date_added : date()
  })
  MERGE (el)-[:HAS_PROPERTY {float_value: toFloat(line.melt)}]->(pmelt)-[:IS_A]->(melt))

FOREACH(x IN CASE WHEN line.density IS NOT NULL THEN [1] END |
  MERGE(pdensity:Property{uid: randomUUID(),
                                   date_added : date()
  })
  MERGE (el)-[:HAS_PROPERTY {float_value: toFloat(line.density)}]->(pdensity)-[:IS_A]->(density))

FOREACH(x IN CASE WHEN line.molarheat IS NOT NULL THEN [1] END |
  MERGE(pmolarheat:Property{uid: randomUUID(),
                                   date_added : date()
  })
  MERGE (el)-[:HAS_PROPERTY {float_value: toFloat(line.number)}]->(pmolarheat)-[:IS_A]->(molarheat))

FOREACH(x IN CASE WHEN toFloat(line.atomic_mass) IS NOT NULL THEN [1] END |
  MERGE(patomicmass:Property{uid: randomUUID(),
                                   date_added : date()
  })
  MERGE (el)-[:HAS_PROPERTY {float_value: toFloat(line.atomic_mass)}]->(patomicmass)-[:IS_A]-(atomicmass));