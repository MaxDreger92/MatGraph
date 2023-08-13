



MATCH (emmo_cs:EMMOMatter{name:"AcetyleneBlack"})<-[:IS_A]-(m:Matter)<-[:HAS_PART]-(material:Matter),
      (device:Matter)-[:IS_A]->(emmo_fc:EMMOMatter{name:"FuelCell"}),
      p = (material)-[:IS_MANUFACTURING_INPUT| IS_MANUFACTURING_OUTPUT*]->(device)
WITH [node in nodes(p) WHERE (node:Matter)] as manufactured_list
UNWIND manufactured_list as manufactured
WITH DISTINCT manufactured ORDER BY manufactured.name
CALL{
    WITH manufactured
    MATCH (manufactured)-[:IS_A]->(manufactured_label:EMMOMatter)
    WITH  manufactured,
          manufactured_label
    MATCH (manufactured)-[property:HAS_PROPERTY]->(property_node)-[:IS_A]->(property_label)
    WITH property_node, property_label, property
    CALL{
        WITH property_node
        MATCH (property_node)<-[:HAS_MEASUREMENT_OUTPUT]-(:Measurement)-[parameter:HAS_PARAMETER]->(:Parameter)-[:IS_A]-(parameter_label:EMMOQuantity)
        RETURN apoc.coll.toSet(collect(apoc.map.merge(apoc.map.fromValues(["name", parameter_label.name]), parameter{.*}))) as parameter_map
    }
    RETURN apoc.coll.toSet(collect(apoc.map.merge(apoc.map.merge(apoc.map.fromValues(["name", property_label.name]), property{.*}),
                                                                apoc.map.fromValues(["parameters", parameter_map])))) as property_list
}
MATCH (manufactured)-[:IS_A]->(manufactured_label:EMMOMatter)
WITH DISTINCT manufactured,
              manufactured_label,
              property_list
OPTIONAL MATCH p1 = ((manufactured_label)-[:EMMO__IS_A*]->(:EMMOMatter))
UNWIND nodes(p1) as alt_nodes
WITH manufactured,
     manufactured_label,
     property_list,
     apoc.coll.toSet(collect(alt_nodes.name)) as alternative_label
WITH apoc.map.merge(apoc.map.fromValues(["label", manufactured_label.name,"alternative_label", alternative_label]), manufactured{.*})
     as manufactured_map, manufactured, property_list
RETURN apoc.coll.toSet(collect(apoc.map.setKey(manufactured_map, "Properties", property_list)))