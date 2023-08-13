LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/MaxDreger92/MatGraphAI/master/mat2devplatform/matgraph/data/lukas/DLS/IrO2-15wt-ic013-1Prop086-066ml_DLS.csv' AS row

MATCH(researcher:Researcher {first_name: row.Researcher})
MATCH(material:Material {name:row.Material})
MATCH(solvent:Molecule {name:row.Solvent})
MATCH(emmo_measurement:EMMOProcess {name: row.Ontology})
MATCH(emmo_hydrodynamicdiameter:EMMOQuantity {name: "HydrodynamicDiameter"})
MATCH(emmo_averagehydrodynamicdiameter:EMMOQuantity {name: "AverageHydrodynamicDiameter"})
MATCH(emmo_hydrodynamicvolume:EMMOQuantity {name: "HydrodynamicVolume"})
MATCH(emmo_volume:EMMOQuantity {name: "Volume"})
MATCH(emmo_intensity:EMMOQuantity {name: "Intensity"})
MATCH(emmo_pdi:EMMOQuantity {name: "PolydispersityIndex"})

MERGE(measurement:Measurement {PIDA: row.PIDA,
                               flag: "findich_dls",
                               date_added: date(),
                               experiment_start: row.`Measurement Date and Time`,
                               experiment_end: row.`Measurement Date and Time`,
                               instrument: row.Instrument})
  ON CREATE
  SET measurement.uid = randomUUID()


MERGE(solvent)-[:IS_MEASUREMENT_INPUT {float_value: toFloat(row.Dillution)}]->(measurement)
MERGE(material)-[:IS_MEASUREMENT_INPUT {float_value: toFloat(row.SampleVol)}]->(measurement)

MERGE(measurement)-[:BY]->(researcher)

MERGE(hydrodynamicdiameter:Property {name: "hydrodynamicdiameter"+row.PIDA, 
                                     flag: "findich_dls",
                                     date_added: date()
})
  ON CREATE
  SET hydrodynamicdiameter.uid = randomUUID()
MERGE(measurement)-[:HAS_MEASUREMENT_OUTPUT {list_value: apoc.convert.fromJsonList(TOFLOAT(row.sizes))}]->(hydrodynamicdiameter)
MERGE(hydrodynamicdiameter)-[:IS_A]->(emmo_hydrodynamicdiameter)

MERGE(averagehydrodynamicdiameter:Property {name: "averagehydrodynamicdiameter"+row.PIDA,
                                            flag: "findich_dls",
                                            date_added: date()
})
  ON CREATE
  SET averagehydrodynamicdiameter.uid = randomUUID()
MERGE(measurement)-[:HAS_MEASUREMENT_OUTPUT {float_value: toFloat(row.`Z-Average (d.nm)`)}]->(averagehydrodynamicdiameter)
MERGE(averagehydrodynamicdiameter)-[:IS_A]->(emmo_averagehydrodynamicdiameter)

MERGE(hydrodynamicvolume:Property {name: "hydrodynamicvolume"+row.PIDA,
                                   flag: "findich_dls",
                                   date_added: date()
})
  ON CREATE
  SET hydrodynamicvolume.uid = randomUUID()
MERGE(measurement)-[:HAS_MEASUREMENT_OUTPUT {list_value: apoc.convert.fromJsonList(TOFLOAT(row.volumes))}]->(hydrodynamicvolume)
MERGE(hydrodynamicvolume)-[:IS_A]->(emmo_hydrodynamicvolume)

MERGE(intensity:Property {name: "intensity"+row.PIDA,
                          flag: "findich_dls",
                          date_added: date()
})
  ON CREATE
  SET intensity.uid = randomUUID()
MERGE(measurement)-[:HAS_MEASUREMENT_OUTPUT]->(intensity)
MERGE(material)-[:HAS_PROPERTY {value: apoc.convert.fromJsonList(TO_FLOAT(row.intensities))}]->(intensity)
MERGE(intensity)-[:IS_A]->(emmo_intensity)







