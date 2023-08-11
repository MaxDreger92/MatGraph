MERGE (pida:PIDA {pida: RandomUUID(),
                  date_added : date()
})
  ON CREATE
  SET pida.uid = randomUUID()
WITH pida
LOAD CSV WITH HEADERS FROM 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTZEMjd6YY4Rqq9EnbHDPM47_A2G44GhaautvVp023wVd7rsAjXLvumMcaUJtURHMb8VxLRlF1GEJ7I/pub?output=csv' AS row




MATCH (EMMO_fcas:EMMOProcess {name: "FuelCellAssembly"}),
      (EMMO_fcfab:EMMOProcess {name: "FuelCellManufacturing"}),
      (EMMO_meaas:EMMOProcess {name: "CCMManufacturing"}),
      (EMMO_membrane:EMMOMatter{name: "Membrane"}),
      (EMMO_mea:EMMOMatter{name: "CCM"}),
      (EMMO_fc:EMMOMatter{name: "FuelCell"}),
      (EMMO_bp:EMMOMatter{name: "BipolarPlate"}),
      (EMMO_carbonsupport:EMMOMatter{name: "AcetyleneBlack"}),
      (EMMO_ionomer:EMMOMatter{name: "AquivionD79-25BS"}),
      (EMMO_anode:EMMOMatter{name: "Anode"}),
      (EMMO_catalyst:EMMOMatter{name: "F50E-HT"}),
      (EMMO_bp:EMMOMatter{name: "BipolarPlate"}),
      (EMMO_PTFE:EMMOMatter{name: "PTFE"}),
      (EMMO_ink:EMMOMatter{name: "CatalystInk"}),
      (EMMO_gdl:EMMOMatter{name: "GasDiffusionLayer"}),
      (EMMO_station:EMMOMatter{name: "Station"}),
      (EMMO_inkfab:EMMOProcess{name: "CatalystInkManufacturing"}),
      (EMMO_loading:EMMOQuantity{name: "CatalystLoading"}),
      (EMMO_ew:EMMOQuantity{name: "EquivalentWeight"}),
      (EMMO_ic:EMMOQuantity{name: "CatalystIonomerRatio"}),
      (EMMO_mill:EMMOQuantity{name: "DryMillingTime"}),
      (EMMO_dt:EMMOQuantity{name: "DryingTemperature"})


// MEA and FC
MERGE(fc:Matter:Device {name: row.`Run #`+"FuelCell",
                 date_added : date()
})
  ON CREATE
  SET fc.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(fc)
MERGE(catink:Matter:Material {name: row.`Run #`+"_ink",
                       date_added : date(),
                       flag: "jasna"
})
  ON CREATE
  SET catink.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(catink)


MERGE(mea:Matter:Component {name: row.`Run #`,
                     date_added : date(),
                     flag: "jasna"
})
  ON CREATE
  SET mea.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(mea)

// Other Components
MERGE(membrane:Matter:Material {name: row.Membrane,
                         date_added : date(),
                         flag: "jasna"
})
  ON CREATE
  SET membrane.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(membrane)

MERGE(bp:Matter:Component {name: row.plates,
                    date_added : date(),
                    flag: "jasna"
})
  ON CREATE
  SET bp.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(bp)

MERGE(gdl:Matter:Component {name: row.GDL,
                     date_added : date(),
                     flag: "jasna"
})
  ON CREATE
  SET gdl.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(gdl)

MERGE(station:Matter:Component {name: row.Station,
                         date_added : date(),
                         flag: "jasna"
})
  ON CREATE
  SET station.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(station)

MERGE(anode:Matter:Material {name: row.Anode,
                      date_added : date(),
                      flag: "jasna"
})
  ON CREATE
  SET anode.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(anode)

MERGE(ionomer:Matter:Material {name: row.Ionomer,
                        date_added : date(),
                        flag: "jasna"
})
  ON CREATE
  SET ionomer.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(ionomer)

MERGE(catalyst:Matter:Material {name: row.Catalyst,
                         date_added : date(),
                         flag: "jasna"
})
  ON CREATE
  SET catalyst.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(catalyst)

MERGE(carbonsupport:Matter:Material {name: row.`Catalyst`+"support",
                              date_added : date(),
                              flag: "jasna"
})
  ON CREATE
  SET carbonsupport.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(carbonsupport)

MERGE(carbonsupport)<-[:HAS_PART]-(catalyst)
MERGE(carbonsupport)-[:IS_A]->(EMMO_carbonsupport)


MERGE(coatingsubstrate:Matter:Material {name: row.`Coating substrate`,
                                 date_added : date(),
                                 flag: "jasna"
})
  ON CREATE
  SET coatingsubstrate.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(coatingsubstrate)



// FC-Manufacturing and MEA-Manufacturing
MERGE(fcfab:Process:Manufacturing {uid: randomUUID(),
                           run_title: row.`Run #` + "_FuellCellManufacturing",
                           DOI: row.DOI,
                           date_added : date(),
                           flag: "jasna"
})
MERGE(pida)-[:CONTAINS]->(fcfab)

MERGE(fcass:Process:Manufacturing {uid: randomUUID(),
                           run_title: row.`Run #`+"_FuelCellAssembly",
                           DOI: row.DOI,
                           date_added : date(),
                           flag: "jasna"
})

MERGE(pida)-[:CONTAINS]->(fcass)

MERGE(meafab:Process:Manufacturing {uid: randomUUID(),
                            run_title: row.`Run #`+"_MEAManufacturing",
                            DOI: row.DOI,
                            date_added : date(),
                            flag: "jasna"
})
MERGE(pida)-[:CONTAINS]->(meafab)

MERGE(inkfab:Process:Manufacturing {run_title: row.`Run #`+ "_InkFabrication",
                            date_added : date(),
                            flag: "jasna"
})
  ON CREATE
  SET inkfab.uid = randomUUID()
MERGE(pida)-[:CONTAINS]->(inkfab)


// Labelling
MERGE(EMMO_meaas)<-[:IS_A]-(meafab)
MERGE(fcass)-[:IS_A]->(EMMO_fcas)
MERGE(inkfab)-[:IS_A]->(EMMO_inkfab)
MERGE(fcfab)-[:IS_A]->(EMMO_fcfab)


MERGE(mea)-[:IS_A]->(EMMO_mea)
MERGE(fc)-[:IS_A]->(EMMO_fc)
MERGE(gdl)-[:IS_A]->(EMMO_gdl)
MERGE(bp)-[:IS_A]->(EMMO_bp)
MERGE(ionomer)-[:IS_A]->(EMMO_ionomer)
MERGE(catalyst)-[:IS_A]->(EMMO_catalyst)
MERGE(anode)-[:IS_A]->(EMMO_anode)
MERGE(membrane)-[:IS_A]->(EMMO_membrane)
MERGE(station)-[:IS_A]->(EMMO_station)
MERGE(coatingsubstrate)-[:IS_A]->(EMMO_PTFE)
MERGE(catink)-[:IS_A]->(EMMO_ink)


//Processing
MERGE(fcfab)-[:HAS_PART]->(fcass)
MERGE(fcfab)-[:HAS_PART]->(meafab)
MERGE(fcfab)-[:HAS_PART]->(inkfab)

MERGE(meafab)-[:FOLLOWED_BY]->(fcass)
MERGE(inkfab)-[:FOLLOWED_BY]->(meafab)

MERGE(catalyst)-[:IS_MANUFACTURING_INPUT]->(inkfab)
MERGE(ionomer)-[:IS_MANUFACTURING_INPUT]->(inkfab)
MERGE(inkfab)-[:IS_MANUFACTURING_OUTPUT]->(catink)

MERGE(meafab)-[:IS_MANUFACTURING_OUTPUT]->(mea)
MERGE(membrane)-[:IS_MANUFACTURING_INPUT]->(meafab)
MERGE(anode)-[:IS_MANUFACTURING_INPUT]->(meafab)
MERGE(catink)-[:IS_MANUFACTURING_INPUT]->(meafab)
MERGE(coatingsubstrate)-[:IS_MANUFACTURING_INPUT]->(meafab)


MERGE(bp)-[:IS_MANUFACTURING_INPUT]->(fcass)
MERGE(mea)-[:IS_MANUFACTURING_INPUT]->(fcass)
MERGE(gdl)-[:IS_MANUFACTURING_INPUT]->(meafab)
MERGE(station)-[:IS_MANUFACTURING_INPUT]->(fcass)
MERGE(fcass)-[:IS_MANUFACTURING_OUTPUT]->(fc)

// Composition
MERGE(ink)-[:HAS_PART]->(catalyst)
MERGE(ink)-[:HAS_PART]->(ionomer)

MERGE(mea)-[:HAS_PART]->(gdl)
MERGE(mea)-[:HAS_PART]->(ink)
MERGE(mea)-[:HAS_PART]->(membrane)
MERGE(mea)-[:HAS_PART]->(anode)

MERGE(fc)-[:HAS_PART]->(mea)
MERGE(fc)-[:HAS_PART]->(station)
MERGE(fc)-[:HAS_PART]->(bp)

MERGE(catink)-[:HAS_PART]->(ionomer)
MERGE(catink)-[:HAS_PART]->(catalyst)

MERGE(catalyst)-[:HAS_PART]->(carbonsupport)




// Properties

MERGE(loading:Process:Measurement{uid: randomUUID(),
                          DOI: row.DOI,
                          date_added : date()
})
MERGE(pida)-[:CONTAINS]->(loading)

MERGE(ploading:Quantity:Property{uid: randomUUID(),
                        DOI: row.DOI,
                        date_added : date()
})
MERGE(pida)-[:CONTAINS]->(ploading)

MERGE(mea)-[:IS_MEASUREMENT_INPUT]->(loading)-[:HAS_MEASUREMENT_OUTPUT]->(ploading)-[:IS_A]->(EMMO_loading)
MERGE(mea)-[:HAS_PROPERTY{
  float_value: TOFLOAT(row.`Pt loading (mg/cm2geo)`)}]->(ploading)

MERGE(ic:Process:Measurement{uid: row.`Run #`,
                     DOI: row.`Run #`,
                     date_added : date()
})
MERGE(pida)-[:CONTAINS]->(ic)

SET ic.uid = randomUUID()
SET ic.DOI = row.DOI
MERGE(pic:Quantity:Property{uid: row.`Run #`,
                   DOI: row.`Run #`,
                   date_added : date()
})
MERGE(pida)-[:CONTAINS]->(pic)

SET pic.uid = randomUUID()
SET pic.DOI = row.DOI

MERGE(catink)-[:IS_MEASUREMENT_INPUT]->(ic)-[:HAS_MEASUREMENT_OUTPUT]->(pic)-[:IS_A]->(EMMO_ic)
MERGE(catink)-[:HAS_PROPERTY{
  float_value: TOFLOAT(row.`I/C`)}]->(pic)


MERGE(ew:Process:Measurement{uid: row.EW,
                     date_added : date()
})
MERGE(pida)-[:CONTAINS]->(ew)

SET ew.uid = randomUUID()
MERGE(pew:Quantity:Property{uid: row.EW,
                   date_added : date()
})

SET pew.uid = randomUUID()
MERGE(ionomer)-[:IS_MEASUREMENT_INPUT]->(ew)-[:HAS_MEASUREMENT_OUTPUT]->(pew)-[:IS_A]->(EMMO_ew)
MERGE(ionomer)-[:HAS_PROPERTY{
  float_value: TOFLOAT(row.`EW`)}]->(pew)
MERGE(pida)-[:CONTAINS]->(pew)

// Paraneters
MERGE(mill:Quantity:Parameter{date_added : date(), uid: randomUUID()})
MERGE(pida)-[:CONTAINS]->(mill)

MERGE(inkfab)-[:HAS_PARAMETER{float_value: TOFLOAT(row.`Drymill time (hrs)`)}]->(mill)
MERGE (mill)-[:IS_A]->(EMMO_mill)
MERGE(dt:Quantity:Parameter{date_added : date(), uid: randomUUID()})
MERGE(pida)-[:CONTAINS]->(dt)
MERGE(meafab)-[:HAS_PARAMETER{float_value: TOFLOAT(row.`Drying temp (deg C)`)}]->(dt)
MERGE (dt)-[:IS_A]->(EMMO_dt)




