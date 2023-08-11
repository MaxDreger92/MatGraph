LOAD CSV WITH HEADERS FROM 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSTqtdK6QfEyQfmKjGwkjmdD91NuerG4N7dwUQwOy9SPgj9m3KX0RhLvLKgyAqaMC9yglLNLd-Eba2_/pub?output=csv' AS row

MATCH (EMMO_ionomer:EMMOMatter{name: "AquivionD79-25BS"})<-[:IS_A]-(ionomer:Matter:Material),
      (ink:Matter:Material {name: row.`Run #`+"_ink"})-[:IS_A]-(:EMMOMatter {name: 'CatalystInk'}),
      (ionomer)<-[:HAS_PART]-(ink),
      (EMMO_carbonsupport:EMMOMatter{name: "AcetyleneBlack"})<-[:IS_A]-(carbon:Matter:Material),
      (carbon)<-[:HAS_PART]-(catalyst)-[:HAS_PART]-(ink),
      (EMMO_epoxy:EMMOMatter{name: 'Polyepoxide'}),
      (EMMO_cathode:EMMOMatter{name: 'Cathode'}),
      (EMMO_thickness:EMMOQuantity{name: 'Thickness'}),
      (EMMO_porosity:EMMOQuantity{name: 'Porosity'}),
      (EMMO_crackdensity:EMMOQuantity{name: 'CrackDensity'}),
      (EMMO_voidvol:EMMOQuantity{name: 'SpecificVolumeVoid'}),
      (EMMO_epoxyfilledvol:EMMOQuantity{name: 'SpecificVolumeSolid'}),
      (EMMO_ionomervol:EMMOQuantity{name: 'SpecificVolumeSolid'}),
      (EMMO_solidvol:EMMOQuantity{name: 'SpecificVolumeSolid'}),
      (EMMO_inaccessiblecarbonfraction:EMMOQuantity{name: 'InaccessiblePoreFraction'}),
      (EMMO_inaccessibleporefraction:EMMOQuantity{name: 'InaccassibleCarbonFraction'}),
      (EMMO_cclfab:EMMOProcess {name: 'CCLManufacturing'}),
      (EMMO_powderdvs:EMMOProcess {name: 'PowderDynamicVaporSorptionMeasurement'}),
      (EMMO_cldvs:EMMOProcess {name: 'CatalystLayerDynamicVaporSorptionMeasurement'}),
      (EMMO_sem:EMMOProcess {name: 'SEMImaging'}),
      (EMMO_tem:EMMOProcess {name: 'TEMImaging'}),
      (EMMO_msp:EMMOProcess {name: 'MethodOfStandardPorosimetry'}),
      (EMMO_rh:EMMOQuantity {name: 'RelativeHumidity'}),
      (EMMO_dvs:EMMOQuantity {name: 'DynamicVaporDesorption'}),
      (EMMO_dvds:EMMOQuantity {name: 'DynamicVaporSorption'}),
      (EMMO_ic:EMMOQuantity{name: "CatalystIonomerRatio"}),
      (EMMO_preparation:EMMOProcess {name: 'SamplePreparation'})

// Process Nodes
MERGE(cclfab:Process:Manufacturing {run_title: row.`Run #`,
                            uid: randomUUID(),
                           DOI: row.DOI
})
ON CREATE
SET cclfab.date_added = date()

MERGE(epoxy)-[:IS_A]->(EMMO_epoxy)
//Matter Nodes
MERGE(ccl:Matter:Material {name: row.`Run #`,
                    uid : randomUUID() })
ON CREATE
SET cclfab.date_added = date()


// Measurement nodes
MERGE(sem:Process:Measurement{uid: randomUUID(),
                     date_added : date()
})
MERGE(keyence:Process:Measurement{uid: randomUUID(),
                      date_added : date()
})
MERGE(thickness:Quantity:Property{uid: randomUUID(),
                      date_added : date()
})
MERGE(porosity:Quantity:Property{uid: randomUUID(),
                         date_added : date()
})
MERGE(voidvol:Quantity:Property{uid: randomUUID(),
                        date_added : date()
})
MERGE(crackdensity:Quantity:Property{uid: randomUUID(),
                       date_added : date()
})
MERGE(ccl)-[:IS_MEASUREMENT_INPUT]->(sem)-[:HAS_MEASUREMENT_OUTPUT]
  ->(thickness)-[:IS_A]->(EMMO_thickness)
MERGE(ccl)-[:HAS_PROPERTY{float_value: tofloat(row.`SEM thickness STD (µm)`), float_std: tofloat(row.`SEM thickness STD (µm)`)}]->(thickness)

MERGE(sem)-[:HAS_MEASUREMENT_OUTPUT]
  ->(porosity)-[:IS_A]->(EMMO_porosity)
MERGE(porosity)-[:DERIVED_FROM]->(thickness)
MERGE(ccl)-[:HAS_PROPERTY{float_value: tofloat(row.`Calculated porosity based on SEM thickness (%)`)}]->(porosity)

MERGE(sem)-[:HAS_MEASUREMENT_OUTPUT]
->(voidvol)-[:IS_A]->(EMMO_voidvol)
MERGE(voidvol)-[:DERIVED_FROM]->(thickness)
MERGE(ccl)-[:HAS_PROPERTY{float_value: tofloat(row.`Calculated PV based on SEM thickness (cm3/cm2geo)`)}]->(voidvol)

MERGE(ccl)-[:IS_MEASUREMENT_INPUT]->(keyence)-[:HAS_MEASUREMENT_OUTPUT]
->(crackdensity)-[:IS_A]->(EMMO_crackdensity)
MERGE(ccl)-[:HAS_PROPERTY{float_value: tofloat(row.`Keyence Crack density 400x mag (%)`)}]->(crackdensity)

FOREACH(x IN CASE WHEN row.`Densometer Porosity (%)` IS NOT NULL THEN [1] END |
  MERGE(densometer:Process:Measurement{uid: randomUUID(),
                        date_added : date()})
  MERGE(dporosity:Quantity:Property{uid: randomUUID(),
                              date_added : date()
  })
  MERGE(dsolidvolume:Quantity:Property{uid: randomUUID(),
                           date_added : date()
  })
  MERGE(dthickness:Quantity:Property{uid: randomUUID(),
                              date_added : date()
  })
  MERGE(dvoidvolume:Quantity:Property{uid: randomUUID(),
                              date_added : date()
  })
  MERGE(ccl)-[:IS_MEASUREMENT_INPUT]->(densometer)-[:HAS_MEASUREMENT_OUTPUT]
  ->(dporosity)-[:IS_A]->(EMMO_porosity)
  MERGE(densometer)-[:HAS_MEASUREMENT_OUTPUT]
  ->(dthickness)-[:IS_A]->(EMMO_thickness)
  MERGE(densometer)-[:HAS_MEASUREMENT_OUTPUT]
  ->(dsolidvolume)-[:IS_A]->(EMMO_solidvol)
  MERGE(densometer)-[:HAS_MEASUREMENT_OUTPUT]
  ->(dvoidvolume)-[:IS_A]->(EMMO_voidvol)
  MERGE(ccl)-[:HAS_PROPERTY{float_value: tofloat(row.`Densometer PV (cm3/cm2geo)`)}]->(dvoidvolume)
  MERGE(ccl)-[:HAS_PROPERTY{float_value: tofloat(row.`Densometer solid volume (cm3/cm2 geo)`)}]->(dsolidvolume)
  MERGE(ccl)-[:HAS_PROPERTY{float_value: tofloat(row.`Densometer CL thickness (µm)`)}]->(dthickness)
  MERGE(ccl)-[:HAS_PROPERTY{float_value: tofloat(row.`Densometer Porosity (%)`)}]->(dporosity)
)

// DVS 50 RH
MERGE(dvs50:Process:Measurement{uid: randomUUID(),
                      date_added : date()
})
MERGE(pdvs50:Quantity:Property{uid: randomUUID(),
                         date_added : date()
})
MERGE(ink)-[:IS_MEASUREMENT_INPUT]->(dvs50)
MERGE(dvs50)-[:IS_A]->(EMMO_powderdvs)
MERGE(dvs50)-[:HAS_MEASUREMENT_OUTPUT]
->(pdvs50)-[:IS_A]->(EMMO_dvs)
CREATE(dvs50)-[:HAS_PARAMETER{float_value: 50}]->(:Quantity:Parameter{uid : randomUUID()})-[:IS_A]->(EMMO_rh)
MERGE(ink)-[:HAS_PROPERTY{float_value: tofloat(row.`Powder DVS soprtion at 50%RH (% mass change/cm2geo)`)}]->(pdvs50)

// DVDS 50 RH
MERGE(dvds50:Process:Measurement{uid: randomUUID(),
                        date_added : date()
})
MERGE(dvds50)-[:IS_A]->(EMMO_powderdvs)
MERGE(ink)-[:IS_MEASUREMENT_INPUT]->(dvds50)
MERGE(pdvds50:Quantity:Property{uid: randomUUID(),
                      date_added : date()
})
MERGE(dvds50)-[:HAS_MEASUREMENT_OUTPUT]
->(pdvds50)-[:IS_A]->(EMMO_dvds)
CREATE(dvds50)-[:HAS_PARAMETER{float_value: 50}]->(:Quantity:Parameter)-[:IS_A]->(EMMO_rh)
MERGE(ink)-[:HAS_PROPERTY{float_value: tofloat(row.`Powder DVS desoprtion at 50%RH (% mass change/cm2geo)`)}]->(pdvds50)


//DVS 95 RH
MERGE(dvs95:Process:Measurement{uid: randomUUID(),
                         date_added : date()
})
MERGE(dvs95)-[:IS_A]->(EMMO_powderdvs)
MERGE(ink)-[:IS_MEASUREMENT_INPUT]->(dvs95)
MERGE(pdvs95:Quantity:Property{uid: randomUUID(),
                       date_added : date()
})
MERGE(dvs95)-[:HAS_MEASUREMENT_OUTPUT]
->(pdvs95)-[:IS_A]->(EMMO_dvs)
CREATE(dvs95)-[:HAS_PARAMETER{float_value: 95}]->(:Quantity:Parameter)-[:IS_A]->(EMMO_rh)
MERGE(ink)-[:HAS_PROPERTY{float_value: tofloat(row.`Powder DVS soprtion at 95%RH (% mass change/cm2geo)`)}]->(pdvs95)


//CL dvds 50 RH
FOREACH(x IN CASE WHEN row.`CL DVS desoprtion at 50%RH (% mass change/cm2geo)` IS NOT NULL THEN [1]
  END |
  MERGE(cldvds50:Process:Measurement{uid:randomUUID(),
                           date_added:date()
  })
  MERGE(cldvds50)-[:IS_A]->(EMMO_cldvs)
  MERGE(ink)- [:IS_MEASUREMENT_INPUT] - >(dvds50)
  MERGE(clpdvds50:Quantity:Property{uid:randomUUID(),
                          date_added:date()
  })
  MERGE(cldvds50)- [:HAS_MEASUREMENT_OUTPUT]
  - >(clpdvds50)- [:IS_A] - >(EMMO_dvds)
  CREATE(cldvds50)- [:HAS_PARAMETER{float_value:50}]- >(:Quantity:Parameter)- [:IS_A] - >(EMMO_rh)
  MERGE(ink)-[:HAS_PROPERTY{float_value:TOFLOAT(row.`CL DVS desoprtion at 50%RH (% mass change/cm2geo)`)}]->(clpdvds50)

)

//CL DVS 50 RH
FOREACH(x IN CASE WHEN row.`CL DVS soprtion at 50%RH (% mass change/cm2geo)` IS NOT NULL THEN [1]
END |
MERGE(cldvs50:Process:Measurement{uid:randomUUID(),
date_added:date()
})
MERGE(cldvs50)-[:IS_A]->(EMMO_cldvs)
MERGE(ink)- [:IS_MEASUREMENT_INPUT] - >(dvs50)
MERGE(clpdvs50:Quantity:Property{uid:randomUUID(),
date_added:date()
})
MERGE(cldvs50)- [:HAS_MEASUREMENT_OUTPUT]
- >(clpdvs50)- [:IS_A] - >(EMMO_dvs)
CREATE(cldvs50)- [:HAS_PARAMETER{float_value:50}]- >(:Quantity:Parameter)- [:IS_A] - >(EMMO_rh)
  MERGE(ink)-[:HAS_PROPERTY{float_value:TOFLOAT(row.`CL DVS soprtion at 50%RH (% mass change/cm2geo)`)}]->(clpdvs50)
)

//CL DVS 95 RH
FOREACH(x IN CASE WHEN row.`CL DVS soprtion at 95%RH (% mass change/cm2geo)` IS NOT NULL THEN [1]
  END |
  MERGE(tem:Process:Measurement{uid:randomUUID(),
                           date_added: date(),
flag: "jasna"
  })
  MERGE(tem)-[:IS_A]->(EMMO_tem)
  MERGE(ink)- [:IS_MEASUREMENT_INPUT] - >(dvs95)
  MERGE(clpdvs95:Quantity:Property{uid:randomUUID(),
                          date_added: date(),
                          flag: "jasna"
  })
  MERGE(cldvs95)- [:HAS_MEASUREMENT_OUTPUT]
  - >(clpdvs95)- [:IS_A] - >(EMMO_dvs)
  CREATE(cldvs95)- [:HAS_PARAMETER{float_value:95}]- >(:Quantity:Parameter)- [:IS_A] - >(EMMO_rh)
  MERGE(ink)-[:HAS_PROPERTY{float_value:TOFLOAT(row.`CL DVS soprtion at 95%RH (% mass change/cm2geo)`)}]->(clpdvs95)

)

FOREACH(x IN CASE WHEN row.`TEM EDX Inaccessible pores (%)` IS NOT NULL THEN [1] END |
  MERGE(epoxy:Matter:Material {uid : randomUUID() ,
        date_added : date(),
        flag: "jasna"
        })
  MERGE(tem:Process:Measurement{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(temic:Quantity:Property{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(temionomervol:Quantity:Property{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(temporosity:Quantity:Property{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(temtotalporosity:Quantity:Property{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(temepoxy:Process:Measurement{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(preparation:Process:Manufacturing{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(preparation)-[:IS_A]->(EMMO_preparation)
  MERGE(temepoxy)-[:HAS_PART]->(preparation)
  MERGE(epoxy)-[:IS_MANUFACTURING_INPUT]->(preparation)
  MERGE(ccl)-[:IS_MANUFACTURING_INPUT]->(preparation)
  MERGE(epoxyccl:Matter:Material {uid : randomUUID() ,
        date_added : date(),
        flag: "jasna"
        })

  MERGE(preparation)-[:IS_MANUFACTURING_OUTPUT]->(epoxyccl)


  MERGE(temepoxyfilledporosity:Quantity:Property{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(teminaccessiblepores:Quantity:Property{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(teminaccessiblecarbon:Quantity:Property{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(temepoxyfilledvolume:Quantity:Property{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(temionomerthickness:Quantity:Property{uid: randomUUID(),
        date_added : date(),
        flag: "jasna"
        })
  MERGE(ccl)- [:IS_MEASUREMENT_INPUT] - >(tem)-[:IS_A]->(EMMO_tem)
  MERGE(ccl)- [:IS_MEASUREMENT_INPUT] - >(temepoxy)-[:IS_A]->(EMMO_tem)
  MERGE(ccl)- [:HAS_PROPERTY{float_value: tofloat(row.`I/C TEM measured`)}] - >(temic)
  MERGE(temic)-[:IS_A]->(EMMO_ic)
  MERGE(tem)- [:HAS_MEASUREMENT_OUTPUT] - >(temionomervol)
  MERGE(ionomer)- [:HAS_PROPERTY{float_value: tofloat(row.`Ionomer volume, cm3/cm2`)}] - >(temionomervol)
  MERGE(temionomervol)-[:IS_A]->(EMMO_ionomervol)
  MERGE(tem)- [:HAS_MEASUREMENT_OUTPUT] - >(temporosity)
  MERGE(ccl)- [:HAS_PROPERTY{float_value: tofloat(row.`Theoretical porosity, based on TEM local thickness and target I/C`)}] - >(temporosity)
  MERGE(temporosity)-[:IS_A]->(EMMO_porosity)
  MERGE(tem)- [:HAS_MEASUREMENT_OUTPUT] - >(temtotalporosity)
  MERGE(ccl)- [:HAS_PROPERTY{float_value: tofloat(row.`TEM EDX Total porosity (%)`)}] - >(temtotalporosity)
  MERGE(temtotalporosity)-[:IS_A]->(EMMO_porosity)
  MERGE(ccl)- [:HAS_PROPERTY{float_value: tofloat(row.`TEM EDX Epoxy-filled porosity (%)`)}] - >(temepoxyfilledporosity)
  MERGE(temepoxy)- [:HAS_MEASUREMENT_OUTPUT] - >(temepoxyfilledporosity)
  MERGE(temepoxyfilledporosity)-[:IS_A]->(EMMO_porosity)
  MERGE(tem)- [:HAS_MEASUREMENT_OUTPUT] - >(teminaccessiblepores)
  MERGE(ccl)- [:HAS_PROPERTY{float_value: tofloat(row.`TEM EDX Inaccessible pores (%)`)}] - >(teminaccessiblepores)
  MERGE(teminaccessiblepores)-[:IS_A]->(EMMO_inaccessibleporefraction)
  MERGE(tem)- [:HAS_MEASUREMENT_OUTPUT] - >(teminaccessiblecarbon)
  MERGE(carbon)- [:HAS_PROPERTY{float_value: tofloat(row.`TEM EDX % of Inaccessible Carbon (%)`)}] - >(teminaccessiblecarbon)
  MERGE(teminaccessiblecarbon)-[:IS_A]->(EMMO_inaccessiblecarbonfraction)
  MERGE(temepoxy)- [:HAS_MEASUREMENT_OUTPUT] - >(temepoxyfilledvolume)
  MERGE(epoxy)- [:HAS_PROPERTY{float_value: tofloat(row.`TEM EDX Epoxy-filled Volume (cm3/cm2 geo)2`)}] - >(temepoxyfilledvolume)
  MERGE(temepoxyfilledvolume)-[:IS_A]->(EMMO_epoxyfilledvol)
  MERGE(tem)- [:HAS_MEASUREMENT_OUTPUT] - >(temionomerthickness)
  MERGE(ionomer)- [:HAS_PROPERTY{float_value: tofloat(row.`TEM EDX effective ionomer thickness deff wrt BET SA (nm)`), std: tofloat(row.`TEM EDX effective ionomer thickness deff std dev (nm)`)}] - >(temionomerthickness)
  MERGE(temionomerthickness)-[:IS_A]->(EMMO_thickness)





)


//Labeling
MERGE(ccl)-[:IS_A]->(EMMO_cathode)
MERGE(cclfab)-[:IS_A]->(EMMO_cclfab)
MERGE(sem)-[:IS_A]->(EMMO_sem)

// Processing
MERGE(ink)-[:IS_MANUFACTURING_INPUT]->(cclfab)
MERGE(cclfab)-[:IS_MANUFACTURING_OUTPUT]->(ccl)