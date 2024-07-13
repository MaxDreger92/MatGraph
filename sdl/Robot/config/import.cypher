// Create the SDL node with a random UUID
CREATE (sdl:SDL {name: "Self-Driving Lab", uuid: randomUUID()})

// Create the slots (zones) for the Opentrons OT-2 robot with slot attribute and random UUID
FOREACH (slot IN range(1, 12) |
  CREATE (s:Zone {name: "Slot " + slot, slot: slot, uuid: randomUUID()})
  CREATE (sdl)-[:HAS_PART]->(s)
);
MERGE (sdl:SDL {name: "Self-Driving Lab"})
// Create the AUTODIAL 25 Reservoir module with a random UUID
CREATE (module1:Module {
  name: "AUTODIAL 25 Reservoir 4620 µL",
  brand: "AUTODIAL",
  brandId: "Daniel",
  displayCategory: "reservoir",
  displayVolumeUnits: "µL",
  xDimension: 127.75,
  yDimension: 85.5,
  zDimension: 51,
  uuid: randomUUID()
})
CREATE (sdl)-[:HAS_MODULE]->(module1)

// Create the wells for the AUTODIAL 25 Reservoir module
WITH module1
UNWIND [
  {name: "B1", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 34.38, y: 57.25, z: 21.5},
  {name: "C1", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 34.38, y: 42.25, z: 21.5},
  {name: "D1", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 34.38, y: 27.25, z: 21.5},
  {name: "A2", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 49.38, y: 72.25, z: 21.5},
  {name: "B2", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 49.38, y: 57.25, z: 21.5},
  {name: "C2", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 49.38, y: 42.25, z: 21.5},
  {name: "D2", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 49.38, y: 27.25, z: 21.5},
  {name: "E2", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 49.38, y: 12.25, z: 21.5},
  {name: "A3", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 64.38, y: 72.25, z: 21.5},
  {name: "B3", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 64.38, y: 57.25, z: 21.5},
  {name: "C3", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 64.38, y: 42.25, z: 21.5},
  {name: "D3", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 64.38, y: 27.25, z: 21.5},
  {name: "E3", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 64.38, y: 12.25, z: 21.5},
  {name: "A4", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 79.38, y: 72.25, z: 21.5},
  {name: "B4", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 79.38, y: 57.25, z: 21.5},
  {name: "C4", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 79.38, y: 42.25, z: 21.5},
  {name: "D4", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 79.38, y: 27.25, z: 21.5},
  {name: "E4", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 79.38, y: 12.25, z: 21.5},
  {name: "B5", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 94.38, y: 57.25, z: 21.5},
  {name: "C5", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 94.38, y: 42.25, z: 21.5},
  {name: "D5", depth: 29.5, totalLiquidVolume: 4620, shape: "circular", diameter: 14, x: 94.38, y: 27.25, z: 21.5}
] AS wellData
CREATE (well:Well {
  name: wellData.name,
  depth: wellData.depth,
  totalLiquidVolume: wellData.totalLiquidVolume,
  shape: wellData.shape,
  diameter: wellData.diameter,
  x: wellData.x,
  y: wellData.y,
  z: wellData.z,
  uuid: randomUUID()
})
CREATE (module1)-[:HAS_PART]->(well);
MERGE (sdl:SDL {name: "Self-Driving Lab"})
// Create the new vial rack module node with a random UUID
CREATE (module2:Module {
  name: "Vial Rack 1",
  brand: "Generic",
  displayCategory: "vial rack",
  uuid: randomUUID()
})
CREATE (sdl)-[:HAS_MODULE]->(module2)

// Calculate typical coordinates for the vial rack wells
WITH module2, [
  {name: "A1", x: 20.0, y: 40.0, z: 0.0},
  {name: "B1", x: 40.0, y: 40.0, z: 0.0},
  {name: "C1", x: 60.0, y: 40.0, z: 0.0},
  {name: "A2", x: 20.0, y: 20.0, z: 0.0},
  {name: "B2", x: 40.0, y: 20.0, z: 0.0},
  {name: "C2", x: 60.0, y: 20.0, z: 0.0}
] AS vialRackWells

// Create the wells for the vial rack module
UNWIND vialRackWells AS wellData
CREATE (well:Well {
  name: wellData.name,
  depth: 25.0,  // Default depth
  totalLiquidVolume: 1500,  // Default volume
  shape: "circular",
  diameter: 12.0,  // Default diameter
  x: wellData.x,
  y: wellData.y,
  z: wellData.z,
  uuid: randomUUID()
})
CREATE (module2)-[:HAS_PART]->(well);
MERGE (sdl:SDL {name: "Self-Driving Lab"})
// Create the new vial rack module node with a random UUID
CREATE (module2:Module {
  name: "Vial Rack 2",
  brand: "Generic",
  displayCategory: "vial rack",
  uuid: randomUUID()
})
CREATE (sdl)-[:HAS_MODULE]->(module2)

// Calculate typical coordinates for the vial rack wells
WITH module2, [
  {name: "A1", x: 20.0, y: 40.0, z: 0.0},
  {name: "B1", x: 40.0, y: 40.0, z: 0.0},
  {name: "C1", x: 60.0, y: 40.0, z: 0.0},
  {name: "A2", x: 20.0, y: 20.0, z: 0.0},
  {name: "B2", x: 40.0, y: 20.0, z: 0.0},
  {name: "C2", x: 60.0, y: 20.0, z: 0.0}
] AS vialRackWells

// Create the wells for the vial rack module
UNWIND vialRackWells AS wellData
CREATE (well:Well {
  name: wellData.name,
  depth: 25.0,  // Default depth
  totalLiquidVolume: 1500,  // Default volume
  shape: "circular",
  diameter: 12.0,  // Default diameter
  x: wellData.x,
  y: wellData.y,
  z: wellData.z,
  uuid: randomUUID()
})
CREATE (module2)-[:HAS_PART]->(well);
MERGE (sdl:SDL {name: "Self-Driving Lab"})
// Create the new vial rack module node with a random UUID
CREATE (module2:Module {
  name: "Vial Rack 3",
  brand: "Generic",
  displayCategory: "vial rack",
  uuid: randomUUID()
})
CREATE (sdl)-[:HAS_MODULE]->(module2)

// Calculate typical coordinates for the vial rack wells
WITH module2, [
  {name: "A1", x: 20.0, y: 40.0, z: 0.0},
  {name: "B1", x: 40.0, y: 40.0, z: 0.0},
  {name: "C1", x: 60.0, y: 40.0, z: 0.0},
  {name: "A2", x: 20.0, y: 20.0, z: 0.0},
  {name: "B2", x: 40.0, y: 20.0, z: 0.0},
  {name: "C2", x: 60.0, y: 20.0, z: 0.0}
] AS vialRackWells

// Create the wells for the vial rack module
UNWIND vialRackWells AS wellData
CREATE (well:Well {
  name: wellData.name,
  depth: 25.0,  // Default depth
  totalLiquidVolume: 1500,  // Default volume
  shape: "circular",
  diameter: 12.0,  // Default diameter
  x: wellData.x,
  y: wellData.y,
  z: wellData.z,
  uuid: randomUUID()
})
CREATE (module2)-[:HAS_PART]->(well);
MERGE (sdl:SDL {name: "Self-Driving Lab"})

// Create the trash module node with a random UUID
CREATE (module3:Module {
  name: "Trash",
  brand: "Generic",
  displayCategory: "trash",
  uuid: randomUUID()
})
CREATE (sdl)-[:HAS_MODULE]->(module3)

// Create the pipette rack module node with a random UUID
CREATE (module4:Module {
  name: "Pipette Rack",
  brand: "Generic",
  displayCategory: "pipette rack",
  uuid: randomUUID()
})
CREATE (sdl)-[:HAS_MODULE]->(module4)

// Create the electrode rack module node with a random UUID
CREATE (module5:Module {
  name: "Electrode Rack",
  brand: "Generic",
  displayCategory: "electrode rack",
  uuid: randomUUID()
})
CREATE (sdl)-[:HAS_MODULE]->(module5)

// Calculate typical coordinates for the electrode rack wells
WITH module5, [
  {name: "A1", x: 20.0, y: 40.0, z: 0.0},
  {name: "B1", x: 40.0, y: 40.0, z: 0.0},
  {name: "A2", x: 20.0, y: 20.0, z: 0.0},
  {name: "B2", x: 40.0, y: 20.0, z: 0.0}
] AS electrodeRackWells

// Create the wells for the electrode rack module
UNWIND electrodeRackWells AS wellData
CREATE (well:Well {
  name: wellData.name,
  depth: 30.0,  // Default depth
  totalLiquidVolume: 2000,  // Default volume
  shape: "circular",
  diameter: 15.0,  // Default diameter
  x: wellData.x,
  y: wellData.y,
  z: wellData.z,
  uuid: randomUUID()
})
CREATE (module5)-[:HAS_PART]->(well);
MERGE (sdl:SDL {name: "Self-Driving Lab"})

// Create the electrode washing station module node with a random UUID
CREATE (module6:Module {
  name: "Electrode Washing Station",
  brand: "Generic",
  displayCategory: "washing station",
  uuid: randomUUID()
})
CREATE (sdl)-[:HAS_MODULE]->(module6)

// Calculate typical coordinates for the electrode washing station wells
WITH module6, [
  {name: "A1", x: 20.0, y: 40.0, z: 0.0},
  {name: "A2", x: 20.0, y: 20.0, z: 0.0}
] AS washingStationWells

// Create the wells for the electrode washing station module
UNWIND washingStationWells AS wellData
CREATE (well:Well {
  name: wellData.name,
  depth: 25.0,  // Default depth
  totalLiquidVolume: 1000,  // Default volume
  shape: "circular",
  diameter: 12.0,  // Default diameter
  x: wellData.x,
  y: wellData.y,
  z: wellData.z,
  uuid: randomUUID()
})
CREATE (module6)-[:HAS_PART]->(well);
// Connect the modules to the respective slots

// Slot 1 - Pipette Rack
MATCH (slot1:Zone {slot: 1}), (pipetteRack:Module {name: "Pipette Rack"})
CREATE (slot1)-[:HAS_MODULE]->(pipetteRack);

// Slot 2 - Vial Rack 1
MATCH (slot2:Zone {slot: 2}), (vialRack1:Module {name: "Vial Rack 1"})
CREATE (slot2)-[:HAS_MODULE]->(vialRack1);

// Slot 3 - Electrode Washing Station
MATCH (slot3:Zone {slot: 3}), (washingStation:Module {name: "Electrode Washing Station"})
CREATE (slot3)-[:HAS_MODULE]->(washingStation);

// Slot 4 - AUTODIAL 25 Reservoir Module
MATCH (slot4:Zone {slot: 4}), (reservoir:Module {name: "AUTODIAL 25 Reservoir 4620 µL"})
CREATE (slot4)-[:HAS_MODULE]->(reservoir);

// Slot 7 - Vial Rack 2
MATCH (slot7:Zone {slot: 7}), (vialRack2:Module {name: "Vial Rack 2"})
CREATE (slot7)-[:HAS_MODULE]->(vialRack2);

// Slot 10 - Electrode Rack
MATCH (slot10:Zone {slot: 10}), (electrodeRack:Module {name: "Electrode Rack"})
CREATE (slot10)-[:HAS_MODULE]->(electrodeRack);

// Slot 11 - Vial Rack 3
MATCH (slot11:Zone {slot: 11}), (vialRack3:Module {name: "Vial Rack 3"})
CREATE (slot11)-[:HAS_MODULE]->(vialRack3);

// Slot 12 - Trash
MATCH (slot12:Zone {slot: 12}), (trash:Module {name: "Trash"})
CREATE (slot12)-[:HAS_MODULE]->(trash);


//// Create the salt matter nodes with attributes
//MATCH (zone:Zone {slot: 2})-[r:HAS_MODULE]->(module:Module {name: "Vial Rack 1"})-[r2:HAS_PART]->(vial:Well {name: "A1"})
//CREATE (nicl:Matter {name: "NiCl", composition: "Ni2Cl", lot: "12345", open_day: "2024-01-01", uuid: randomUUID()})
//CREATE (edta:Matter {name: "EDTA", composition: "C10H16N2O8", uuid: randomUUID()})
//CREATE (hcl:Matter {name: "HCl", composition: "HCl", uuid: randomUUID()})
//CREATE (dissolution:Manufacturing {name: "Dissolution", uuid: randomUUID()})
//CREATE (solution_nicl:Matter {name: "NiCl Solution", uuid: randomUUID()})
//CREATE (nicl)-[:IS_MANUFACTURING_INPUT]->(dissolution)
//CREATE (edta)-[:IS_MANUFACTURING_INPUT]->(dissolution)
//CREATE (hcl)-[:IS_MANUFACTURING_INPUT]->(dissolution)
//CREATE (dissolution)-[:HAS_MANUFACTURING_OUTPUT]->(solution_nicl)
//CREATE (vol:Property {name: "Volume", value: 1000, unit: "µL", uuid: randomUUID()})
//CREATE (solution_nicl)-[:HAS_PROPERTY]->(vol)
//CREATE (solution_nicl)-[:IN]->(vial)
//CREATE (pur:Property {name: "Purity", value: 99.5, unit: "%", uuid: randomUUID()})
//CREATE (nicl)-[:HAS_PROPERTY]->(pur)
//;

MATCH (zone:Zone {slot: 7})-[r:HAS_MODULE]->(module:Module {name: "Vial Rack 2"})-[r2:HAS_PART]->(vial:Well {name: "A2"})
CREATE (fecl:Matter {name: "NiCl", composition: "Ni2Cl", lot: "12346", open_day: "2024-01-02", uuid: randomUUID()})
CREATE (dissolution:Manufacturing {name: "Dissolution", uuid: randomUUID()})

CREATE (dpta:Matter {name: "DPTA", composition: "C14H23N3O10", uuid: randomUUID()})
CREATE (naoh:Matter {name: "NaOH", composition: "NaOH", uuid: randomUUID()})
CREATE (solution_fecl:Matter {name: "NiCl Solution", uuid: randomUUID()})
CREATE (fecl)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (dpta)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (naoh)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (dissolution)-[:HAS_MANUFACTURING_OUTPUT]->(solution_fecl)
CREATE (vol:Property {name: "Volume", value: 1000, unit: "µL", uuid: randomUUID()})
CREATE (solution_fecl)-[:HAS_PROPERTY]->(vol)
CREATE (solution_fecl)-[:IN]->(vial)
CREATE (pur:Property {name: "Purity", value: 98.0, unit: "%", uuid: randomUUID()})
CREATE (fecl)-[:HAS_PROPERTY]->(pur)
;

MATCH (zone:Zone {slot: 11})-[r:HAS_MODULE]->(module:Module {name: "Vial Rack 3"})-[r2:HAS_PART]->(vial:Well {name: "A1"})
CREATE (cocl:Matter {name: "FeCl", composition: "Fe2Cl", lot: "12347", open_day: "2024-01-03", uuid: randomUUID()})
CREATE (dissolution:Manufacturing {name: "Dissolution", uuid: randomUUID()})

CREATE (edta:Matter {name: "EDTA", composition: "C10H16N2O8", uuid: randomUUID()})
CREATE (hcl:Matter {name: "HCl", composition: "HCl", uuid: randomUUID()})
CREATE (solution_cocl:Matter {name: "CoCl Solution", uuid: randomUUID()})
CREATE (cocl)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (edta)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (hcl)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (dissolution)-[:HAS_MANUFACTURING_OUTPUT]->(solution_cocl)
CREATE (solution_cocl)-[:IN]->(vial)
CREATE (vol:Property {name: "Volume", value: 1000, unit: "µL", uuid: randomUUID()})
CREATE (solution_cocl)-[:HAS_PROPERTY]->(vol)
CREATE (pur:Property {name: "Purity", value: 97.5, unit: "%", uuid: randomUUID()})
CREATE (cocl)-[:HAS_PROPERTY]->(pur)
;

MATCH (zone:Zone {slot: 11})-[r:HAS_MODULE]->(module:Module {name: "Vial Rack 3"})-[r2:HAS_PART]->(vial:Well {name: "B1"})
CREATE (mncl:Matter {name: "CoCl", composition: "Co2Cl", lot: "12348", open_day: "2024-01-04", uuid: randomUUID()})
CREATE (dissolution:Manufacturing {name: "Dissolution", uuid: randomUUID()})

CREATE (dpta:Matter {name: "DPTA", composition: "C14H23N3O10", uuid: randomUUID()})
CREATE (naoh:Matter {name: "NaOH", composition: "NaOH", uuid: randomUUID()})
CREATE (solution_mncl:Matter {name: "MnCl Solution", uuid: randomUUID()})
CREATE (mncl)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (dpta)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (naoh)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (dissolution)-[:HAS_MANUFACTURING_OUTPUT]->(solution_mncl)
CREATE (solution_mncl)-[:IN]->(vial)
CREATE (vol:Property {name: "Volume", value: 1000, unit: "µL", uuid: randomUUID()})
CREATE (solution_mncl)-[:HAS_PROPERTY]->(vol)
CREATE (pur:Property {name: "Purity", value: 99.0, unit: "%", uuid: randomUUID()})
CREATE (mncl)-[:HAS_PROPERTY]->(pur)
;

MATCH (zone:Zone {slot: 11})-[r:HAS_MODULE]->(module:Module {name: "Vial Rack 3"})-[r2:HAS_PART]->(vial:Well {name: "B2"})
CREATE (crcl:Matter {name: "MnCl", composition: "Mn2Cl", lot: "12349", open_day: "2024-01-05", uuid: randomUUID()})
CREATE (dissolution:Manufacturing {name: "Dissolution", uuid: randomUUID()})

CREATE (edta:Matter {name: "EDTA", composition: "C10H16N2O8", uuid: randomUUID()})
CREATE (hcl:Matter {name: "HCl", composition: "HCl", uuid: randomUUID()})
CREATE (solution_crcl:Matter {name: "CrCl Solution", uuid: randomUUID()})
CREATE (crcl)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (edta)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (hcl)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (dissolution)-[:HAS_MANUFACTURING_OUTPUT]->(solution_crcl)
CREATE (solution_crcl)-[:IN]->(vial)
CREATE (vol:Property {name: "Volume", value: 1000, unit: "µL", uuid: randomUUID()})
CREATE (solution_crcl)-[:HAS_PROPERTY]->(vol)
CREATE (pur:Property {name: "Purity", value: 99.7, unit: "%", uuid: randomUUID()})
CREATE (crcl)-[:HAS_PROPERTY]->(pur)
;

MATCH (zone:Zone {slot: 11})-[r:HAS_MODULE]->(module:Module {name: "Vial Rack 3"})-[r2:HAS_PART]->(vial:Well {name: "C2"})
CREATE (cucl:Matter {name: "CuCl", composition: "Cu2Cl", lot: "12350", open_day: "2024-01-06", purity: 98.5, uuid: randomUUID()})
CREATE (dissolution:Manufacturing {name: "Dissolution", uuid: randomUUID()})

CREATE (dpta:Matter {name: "DPTA", composition: "C14H23N3O10", uuid: randomUUID()})
CREATE (naoh:Matter {name: "NaOH", composition: "NaOH", uuid: randomUUID()})
CREATE (solution_cucl:Matter {name: "CuCl Solution", uuid: randomUUID()})
CREATE (cucl)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (dpta)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (naoh)-[:IS_MANUFACTURING_INPUT]->(dissolution)
CREATE (dissolution)-[:HAS_MANUFACTURING_OUTPUT]->(solution_cucl)
CREATE (solution_cucl)-[:IN]->(vial)
CREATE (vol:Property {name: "Volume", value: 1000, unit: "µL", uuid: randomUUID()})
CREATE (solution_cucl)-[:HAS_PROPERTY]->(vol)
CREATE (pur:Property {name: "Purity", value: 98.5, unit: "%", uuid: randomUUID()})
CREATE (cucl)-[:HAS_PROPERTY]->(pur)
;
MATCH (zone:Zone {slot: 10})-[r:HAS_MODULE]->(module:Module {name: "Electrode Rack"})-[r2:HAS_PART]->(well:Well {name: "A1"})
CREATE (counter_electrode:Matter {name: "Counter Electrode", uuid: randomUUID()})
CREATE (counter_electrode)-[:IN]->(well);

MATCH (zone:Zone {slot: 10})-[r:HAS_MODULE]->(module:Module {name: "Electrode Rack"})-[r2:HAS_PART]->(well:Well {name: "A2"})
CREATE (reference_electrode:Matter {name: "Reference Electrode", uuid: randomUUID()})
CREATE (reference_electrode)-[:IN]->(well);

MATCH (zone:Zone {slot: 4})-[r:HAS_MODULE]->(module:Module {name: "AUTODIAL 25 Reservoir 4620 µL"})-[r2:HAS_PART]->(well:Well {name: "E2"})


// Locate the target well for the final mixture

// Mix the first solution
MATCH (solution1:Matter {name: "NiCl Solution"})
CREATE (mixture1:Matter {name: "Mixture 1", uuid: randomUUID()})
CREATE (mixing1:Manufacturing {name: "Mixing", uuid: randomUUID()})
CREATE (solution1)-[:IS_MANUFACTURING_INPUT]->(mixing1)
CREATE (mixing1)-[:HAS_MANUFACTURING_OUTPUT]->(mixture1)
CREATE (mixture1)-[:IN]->(well);

MATCH (zone:Zone {slot: 3})-[r:HAS_MODULE]->(module:Module {name: "Electrode Washing Station"})-[r2:HAS_PART]->(well:Well {name: "A1"})
CREATE (hcl:Matter {name: "HCl", composition: "HCl", uuid: randomUUID()})
CREATE (hcl)-[:IN]->(well);


MATCH (zone:Zone {slot: 4})-[r:HAS_MODULE]->(module:Module {name: "AUTODIAL 25 Reservoir 4620 µL"})-[r2:HAS_PART]->(well:Well {name: "E2"})

// Mix the second solution with the first mixture
MATCH (solution2:Matter {name: "CoCl Solution"})
MATCH (mixture1:Matter {name: "Mixture 1"})
CREATE (mixing2:Manufacturing {name: "Mixing", uuid: randomUUID()})
CREATE (mixture2:Matter {name: "Mixture 2", uuid: randomUUID()})
CREATE (mixture1)-[:IS_MANUFACTURING_INPUT]->(mixing2)
CREATE (solution2)-[:IS_MANUFACTURING_INPUT]->(mixing2)
CREATE (mixing2)-[:HAS_MANUFACTURING_OUTPUT]->(mixture2)
CREATE (mixture2)-[:IN]->(well);

MATCH (zone:Zone {slot: 4})-[r:HAS_MODULE]->(module:Module {name: "AUTODIAL 25 Reservoir 4620 µL"})-[r2:HAS_PART]->(well:Well {name: "E2"})

// Mix the third solution with the second mixture
MATCH (solution3:Matter {name: "MnCl Solution"})
MATCH (mixture2:Matter {name: "Mixture 2"})
CREATE (mixture3:Matter {name: "Mixture 3", uuid: randomUUID()})
CREATE (mixing3:Manufacturing {name: "Mixing", uuid: randomUUID()})
CREATE (mixture2)-[:IS_MANUFACTURING_INPUT]->(mixing3)
CREATE (solution3)-[:IS_MANUFACTURING_INPUT]->(mixing3)
CREATE (mixing3)-[:HAS_MANUFACTURING_OUTPUT]->(mixture3)
CREATE (mixture3)-[:IN]->(well);
MATCH (zone:Zone {slot: 4})-[r:HAS_MODULE]->(module:Module {name: "AUTODIAL 25 Reservoir 4620 µL"})-[r2:HAS_PART]->(well:Well {name: "E2"})

// Mix the fourth solution with the third mixture
MATCH (solution4:Matter {name: "CrCl Solution"})
MATCH (mixture3:Matter {name: "Mixture 3"})
CREATE (mixture4:Matter {name: "Mixture 4", uuid: randomUUID()})
CREATE (mixing4:Manufacturing {name: "Mixing", uuid: randomUUID()})

CREATE (mixture3)-[:IS_MANUFACTURING_INPUT]->(mixing4)
CREATE (solution4)-[:IS_MANUFACTURING_INPUT]->(mixing4)
CREATE (mixing4)-[:HAS_MANUFACTURING_OUTPUT]->(mixture4)
CREATE (mixture4)-[:IN]->(well);

// Mix the fifth solution with the fourth mixture
MATCH (solution5:Matter {name: "CuCl Solution"})
MATCH (zone:Zone {slot: 4})-[r:HAS_MODULE]->(module:Module {name: "AUTODIAL 25 Reservoir 4620 µL"})-[r2:HAS_PART]->(well:Well {name: "E2"})
MATCH (mixture4:Matter {name: "Mixture 4"})
WITH DISTINCT solution5, mixture4, well
CREATE (mixture5:Matter {name: "Final Mixture", uuid: randomUUID()})
CREATE (mixing5:Manufacturing {name: "Mixing", uuid: randomUUID()})
CREATE (mixture4)-[:IS_MANUFACTURING_INPUT]->(mixing5)
CREATE (solution5)-[:IS_MANUFACTURING_INPUT]->(mixing5)
CREATE (mixing5)-[:HAS_MANUFACTURING_OUTPUT]->(mixture5)
CREATE (mixture5)-[:IN]->(well);



// Block 1: Measurement 1 and Cleaning 1

// Create cleaned counter electrode and working electrode
CALL {
CREATE (cleaned_counter_electrode:Matter {name: "Cleaned Counter Electrode", uuid: randomUUID()})
CREATE (working_electrode:Matter {name: "Working Electrode", uuid: randomUUID()})
RETURN cleaned_counter_electrode, working_electrode
}
WITH cleaned_counter_electrode, working_electrode

// Match the necessary nodes and create the electrodeposition process
CALL {
MATCH (final_mixture:Matter {name: "Final Mixture"})-[:IN]->(well)
MATCH (counter_electrode:Matter {name: "Counter Electrode"})
MATCH (reference_electrode:Matter {name: "Reference Electrode"})
MATCH(working_electrode:Matter {name: "Working Electrode"})
CREATE (processed_mixture:Matter {name: "Processed Mixture", uuid: randomUUID()})-[:IN]->(well)
CREATE (surface:Matter {name: "Surface", uuid: randomUUID()})-[:IN]->(well)
CREATE (working_electrode)-[:IN]->(well)
CREATE (manufacturing1:Manufacturing {name: "Electrodeposition", uuid: randomUUID()})
CREATE (parameter1:Parameter {name: "Parameter 1", value: "Value 1", unit: "Unit 1", uuid: randomUUID()})
CREATE (final_mixture)-[:IS_MANUFACTURING_INPUT]->(manufacturing1)
CREATE (manufacturing1)-[:HAS_PARAMETER]->(parameter1)
CREATE (counter_electrode)-[:IS_MANUFACTURING_INPUT]->(manufacturing1)
CREATE (reference_electrode)-[:IS_MANUFACTURING_INPUT]->(manufacturing1)
CREATE (manufacturing1)-[:HAS_MANUFACTURING_OUTPUT]->(surface)
CREATE(manufacturing1)-[:HAS_MANUFACTURING_OUTPUT]->(processed_mixture)
RETURN manufacturing1
}
WITH manufacturing1, cleaned_counter_electrode

// Match the necessary nodes and create the cleaning process
CALL {
MATCH (counter_electrode:Matter {name: "Counter Electrode"})
MATCH (well:Well {name: "A1"})<-[:IN]-(water:Matter {name: "HCl"})
CREATE (cleaning1:Manufacturing {name: "Cleaning 1", uuid: randomUUID()})
CREATE (cleaned_counter_electrode:Matter {name: "Cleaned Counter Electrode", uuid: randomUUID()})
CREATE (cleaning1)<-[:IS_MANUFACTURING_INPUT]-(water)
CREATE (cleaning1)<-[:IS_MANUFACTURING_INPUT]-(counter_electrode)
CREATE (cleaning1)-[:HAS_MANUFACTURING_OUTPUT]->(cleaned_counter_electrode)
RETURN cleaning1
}
WITH *
CALL {
MATCH(reference_electrode:Matter {name: "Reference Electrode"})
MATCH (well:Well {name: "A1"})<-[:IN]-(water:Matter {name: "HCl"})
CREATE (cleaning2:Manufacturing {name: "Cleaning 2", uuid: randomUUID()})
CREATE (cleaned_reference_electrode:Matter {name: "Cleaned Reference Electrode", uuid: randomUUID()})
CREATE (cleaning2)<-[:IS_MANUFACTURING_INPUT]-(water)
CREATE (cleaning2)<-[:IS_MANUFACTURING_INPUT]-(reference_electrode)
CREATE (cleaning2)-[:HAS_MANUFACTURING_OUTPUT]->(cleaned_reference_electrode)
RETURN cleaning2
}
RETURN *
;

// Block 1: Measurement 1 and Cleaning 1
//MATCH (final_mixture:Matter {name: "Final Mixture"})
//MATCH (counter_electrode:Matter {name: "Counter Electrode"})
//MATCH (reference_electrode:Matter {name: "Reference Electrode"})
//MATCH (well:Well {name: "A1"})<-[:IN]-(water:Matter {name: "HCl"})
//WITH DISTINCT final_mixture, counter_electrode, reference_electrode, water
//CALL {
//CREATE (cleaned_reference_electrode:Matter {name: "Cleaned Reference Electrode 1", uuid: randomUUID()})
//CREATE (cleaned_counter_electrode:Matter {name: "Cleaned Counter Electrode 1", uuid: randomUUID()})
//CREATE (working_electrode:Matter {name: "Working Electrode 1", uuid: randomUUID()})
//CREATE (measurement1:Measurement {name: "Measurement 1", uuid: randomUUID()})
//CREATE (property1:Property {name: "Property 2", value: "Value 2", unit: "Unit 2", uuid: randomUUID()})
//CREATE (final_mixture)-[:IS_MEASUREMENT_INPUT]->(measurement1)
//CREATE (measurement1)-[:HAS_PROPERTY]->(property1)
//CREATE (working_electrode)-[:IS_MEASUREMENT_INPUT]->(measurement1)
//CREATE (counter_electrode)-[:IS_MEASUREMENT_INPUT]->(measurement1)
//CREATE (reference_electrode)-[:IS_MEASUREMENT_INPUT]->(measurement1)
//RETURN measurement1, cleaned_counter_electrode, cleaned_reference_electrode
//}
//WITH measurement1, cleaned_counter_electrode, cleaned_reference_electrode
//
//CALL {
//CREATE (cleaning1:Manufacturing {name: "Cleaning 2", uuid: randomUUID()})
//CREATE (cleaning1)-[:IS_MANUFACTURING_INPUT]->(water)
//CREATE (cleaning1)-[:IS_MANUFACTURING_INPUT]->(counter_electrode)
//CREATE (cleaning1)-[:IS_MANUFACTURING_INPUT]->(reference_electrode)
//CREATE (cleaning1)-[:HAS_MANUFACTURING_OUTPUT]->(cleaned_counter_electrode)
//CREATE (cleaning1)-[:HAS_MANUFACTURING_OUTPUT]->(cleaned_reference_electrode)
//RETURN cleaning1
//}
//WITH cleaned_counter_electrode, cleaned_reference_electrode
//
//// Block 2: Measurement 2 and Cleaning 2
//MATCH (final_mixture:Matter {name: "Final Mixture"})
//MATCH (counter_electrode:Matter {name: "Cleaned Counter Electrode 1"})
//MATCH (reference_electrode:Matter {name: "Cleaned Reference Electrode 1"})
//MATCH (well:Well {name: "A1"})<-[:IN]-(water:Matter {name: "HCl"})
//WITH DISTINCT final_mixture, counter_electrode, reference_electrode, water
//CALL {
//CREATE (cleaned_reference_electrode:Matter {name: "Cleaned Reference Electrode 2", uuid: randomUUID()})
//CREATE (cleaned_counter_electrode:Matter {name: "Cleaned Counter Electrode 2", uuid: randomUUID()})
//CREATE (measurement2:Measurement {name: "Measurement 2", uuid: randomUUID()})
//CREATE (property2:Property {name: "Property 3", value: "Value 3", unit: "Unit 3", uuid: randomUUID()})
//CREATE (final_mixture)-[:HAS_MEASUREMENT]->(measurement2)
//CREATE (measurement2)-[:HAS_PROPERTY]->(property2)
//CREATE (counter_electrode)-[:IS_MEASUREMENT_INPUT]->(measurement2)
//CREATE (reference_electrode)-[:IS_MEASUREMENT_INPUT]->(measurement2)
//RETURN measurement2, cleaned_counter_electrode, cleaned_reference_electrode
//}
//WITH measurement2, cleaned_counter_electrode, cleaned_reference_electrode
//
//CALL {
//CREATE (cleaning2:Manufacturing {name: "Cleaning 3", uuid: randomUUID()})
//CREATE (cleaning2)-[:IS_MANUFACTURING_INPUT]->(water)
//CREATE (cleaning2)-[:IS_MANUFACTURING_INPUT]->(counter_electrode)
//CREATE (cleaning2)-[:IS_MANUFACTURING_INPUT]->(reference_electrode)
//CREATE (cleaning2)-[:HAS_MANUFACTURING_OUTPUT]->(cleaned_counter_electrode)
//CREATE (cleaning2)-[:HAS_MANUFACTURING_OUTPUT]->(cleaned_reference_electrode)
//RETURN cleaning2
//}
//WITH cleaned_counter_electrode, cleaned_reference_electrode
//
//// Block 3: Measurement 3 and Cleaning 3
//MATCH (final_mixture:Matter {name: "Final Mixture"})
//MATCH (counter_electrode:Matter {name: "Cleaned Counter Electrode 2"})
//MATCH (reference_electrode:Matter {name: "Cleaned Reference Electrode 2"})
//MATCH (well:Well {name: "A1"})<-[:IN]-(water:Matter {name: "HCl"})
//WITH DISTINCT final_mixture, counter_electrode, reference_electrode, water
//CALL {
//CREATE (cleaned_reference_electrode:Matter {name: "Cleaned Reference Electrode 3", uuid: randomUUID()})
//CREATE (cleaned_counter_electrode:Matter {name: "Cleaned Counter Electrode 3", uuid: randomUUID()})
//CREATE (measurement3:Measurement {name: "Measurement 3", uuid: randomUUID()})
//CREATE (property3:Property {name: "Property 4", value: "Value 4", unit: "Unit 4", uuid: randomUUID()})
//CREATE (final_mixture)-[:HAS_MEASUREMENT]->(measurement3)
//CREATE (measurement3)-[:HAS_PROPERTY]->(property3)
//CREATE (counter_electrode)-[:IS_MEASUREMENT_INPUT]->(measurement3)
//CREATE (reference_electrode)-[:IS_MEASUREMENT_INPUT]->(measurement3)
//RETURN measurement3, cleaned_counter_electrode, cleaned_reference_electrode
//}
//WITH measurement3, cleaned_counter_electrode, cleaned_reference_electrode
//
//CALL {
//CREATE (cleaning3:Manufacturing {name: "Cleaning 4", uuid: randomUUID()})
//CREATE (cleaning3)-[:IS_MANUFACTURING_INPUT]->(water)
//CREATE (cleaning3)-[:IS_MANUFACTURING_INPUT]->(counter_electrode)
//CREATE (cleaning3)-[:IS_MANUFACTURING_INPUT]->(reference_electrode)
//CREATE (cleaning3)-[:HAS_MANUFACTURING_OUTPUT]->(cleaned_counter_electrode)
//CREATE (cleaning3)-[:HAS_MANUFACTURING_OUTPUT]->(cleaned_reference_electrode)
//RETURN cleaning3
//}
//RETURN *