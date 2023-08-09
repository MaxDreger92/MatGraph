GEHT!

MATCH
  (onto_node1:EMMOMatter {uid: 'effaff5ece09485c9b8690fae2aaacee'})<-[:IS_A]-(node1:Matter),
  (onto_node2:EMMOProcess {uid: '8b9f48e9629449b9955c1a5fd939ff2e'})<-[:IS_A]-(node2:Process)
  WHERE
  onto_node1.uid = 'effaff5ece09485c9b8690fae2aaacee' AND
  onto_node2.uid = '8b9f48e9629449b9955c1a5fd939ff2e' AND
  (node1)-[:IS_MANUFACTURING_INPUT]->(node2)AND
  (node1)-[:IS_MANUFACTURING_INPUT]->(node2)
WITH
  onto_node1 as onto_node1, node1 as node1, collect({name: coalesce(onto_node1.name, 'N/A'), value: coalesce(onto_node1.description, 'N/A')}) as node1_information,
  onto_node2 as onto_node2, node2 as node2, collect({name: coalesce(onto_node2.name, 'N/A'), value: coalesce(onto_node2.description, 'N/A')}) as node2_information
CALL{ with node1
OPTIONAL MATCH
  (node1)-[node1_p:HAS_PROPERTY]->(node1_property:Quantity)-[:IS_A]->(node1_property_label:EMMOQuantity)
WITH *, collect({name: coalesce(node1_property_label.name, 'N/A'), value: coalesce(node1_p.float_value, 'N/A')}) as node1_properties
RETURN node1_properties
}
CALL
{
with node2
OPTIONAL MATCH
  (node2)-[node2_p:HAS_PARAMETER]->(node2_parameter:Quantity)-[:IS_A]->(node2_parameter_label:EMMOQuantity)
RETURN collect({name: coalesce(node2_parameter_label.name, 'N/A'), value: coalesce(node2_p.float_value, 'N/A')}) as node2_parameters

}

RETURN DISTINCT
  node1_information as node1_information,
  node1_properties,
  node2_information as node2_information, node2_parameters


GEHT NICHT

MATCH
  (onto_node1:EMMOMatter {uid: 'effaff5ece09485c9b8690fae2aaacee'})<-[:IS_A]-(node1:Matter),
  (onto_node2:EMMOProcess {uid: '8b9f48e9629449b9955c1a5fd939ff2e'})<-[:IS_A]-(node2:Process)
  WHERE
  onto_node1.uid = 'effaff5ece09485c9b8690fae2aaacee' AND
  onto_node2.uid = '8b9f48e9629449b9955c1a5fd939ff2e' AND
  (node1)-[:IS_MANUFACTURING_INPUT]->(node2)AND
  (node1)-[:IS_MANUFACTURING_INPUT]->(node2)
WITH
  onto_node1 as onto_node1, node1 as node1, collect({name: coalesce(onto_node1.name, 'N/A'), value: coalesce(onto_node1.description, 'N/A')}) as node1_information,
  onto_node2 as onto_node2, node2 as node2, collect({name: coalesce(onto_node2.name, 'N/A'), value: coalesce(onto_node2.description, 'N/A')}) as node2_information
CALL{ with node1
OPTIONAL MATCH
  (node1)-[node1_p:HAS_PROPERTY]->(node1_property:Quantity)-[:IS_A]->(node1_property_label:EMMOQuantity)
WITH *, collect({name: coalesce(node1_property_label.name, 'N/A'), value: coalesce(node1_p.float_value, 'N/A')}) as node1_properties
RETURN node1_properties
}
OPTIONAL MATCH
  (node2)-[node2_p:HAS_PARAMETER]->(node2_parameter:Quantity)-[:IS_A]->(node2_parameter_label:EMMOQuantity)
WITH *, collect({name: coalesce(node2_parameter_label.name, 'N/A'), value: coalesce(node2_p.float_value, 'N/A')}) as node2_parameters
RETURN DISTINCT
  node1_information as node1_information,
  node1_properties,
  node2_information as node2_information, node2_parameters
