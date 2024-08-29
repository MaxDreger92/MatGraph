MATCH (onto_04fc99764ff440e2982ad556b0fb4355: EMMOMatter {uid: 'ae43adedcc6d46a287938e09c8429b82'}), (onto_aad6c4592a8b43ffb9adaf5084e0d72b: EMMOProcess {uid: 'b18ec338d6a444a080479d13dba283fc'}), (onto_e62ce51afb504305bda3093b2a0e76c4: EMMOMatter {uid: '3c3d0b2ce89a4be587019ed40a98c321'})
CALL {
WITH onto_04fc99764ff440e2982ad556b0fb4355
OPTIONAL MATCH (onto_04fc99764ff440e2982ad556b0fb4355)<-[:EMMO__IS_A*..]-(tree_onto_04fc99764ff440e2982ad556b0fb4355:EMMOMatter)
RETURN collect(DISTINCT tree_onto_04fc99764ff440e2982ad556b0fb4355) + collect(DISTINCT onto_04fc99764ff440e2982ad556b0fb4355) AS combined_04fc99764ff440e2982ad556b0fb4355
}
CALL {
WITH onto_aad6c4592a8b43ffb9adaf5084e0d72b
OPTIONAL MATCH (onto_aad6c4592a8b43ffb9adaf5084e0d72b)<-[:EMMO__IS_A*..]-(tree_onto_aad6c4592a8b43ffb9adaf5084e0d72b:EMMOProcess)
RETURN collect(DISTINCT tree_onto_aad6c4592a8b43ffb9adaf5084e0d72b) + collect(DISTINCT onto_aad6c4592a8b43ffb9adaf5084e0d72b) AS combined_aad6c4592a8b43ffb9adaf5084e0d72b
}
CALL {
WITH onto_e62ce51afb504305bda3093b2a0e76c4
OPTIONAL MATCH (onto_e62ce51afb504305bda3093b2a0e76c4)<-[:EMMO__IS_A*..]-(tree_onto_e62ce51afb504305bda3093b2a0e76c4:EMMOMatter)
RETURN collect(DISTINCT tree_onto_e62ce51afb504305bda3093b2a0e76c4) + collect(DISTINCT onto_e62ce51afb504305bda3093b2a0e76c4) AS combined_e62ce51afb504305bda3093b2a0e76c4
}
CALL {
WITH combined_04fc99764ff440e2982ad556b0fb4355
UNWIND combined_04fc99764ff440e2982ad556b0fb4355 AS full_onto_04fc99764ff440e2982ad556b0fb4355
MATCH (full_onto_04fc99764ff440e2982ad556b0fb4355)<-[:IS_A]-(node_04fc99764ff440e2982ad556b0fb4355:Matter)
RETURN collect(DISTINCT node_04fc99764ff440e2982ad556b0fb4355) AS nodes_04fc99764ff440e2982ad556b0fb4355
}
CALL {
WITH combined_aad6c4592a8b43ffb9adaf5084e0d72b
UNWIND combined_aad6c4592a8b43ffb9adaf5084e0d72b AS full_onto_aad6c4592a8b43ffb9adaf5084e0d72b
MATCH (full_onto_aad6c4592a8b43ffb9adaf5084e0d72b)<-[:IS_A]-(node_aad6c4592a8b43ffb9adaf5084e0d72b:Manufacturing)
RETURN collect(DISTINCT node_aad6c4592a8b43ffb9adaf5084e0d72b) AS nodes_aad6c4592a8b43ffb9adaf5084e0d72b
}
CALL {
WITH combined_e62ce51afb504305bda3093b2a0e76c4
UNWIND combined_e62ce51afb504305bda3093b2a0e76c4 AS full_onto_e62ce51afb504305bda3093b2a0e76c4
MATCH (full_onto_e62ce51afb504305bda3093b2a0e76c4)<-[:IS_A]-(node_e62ce51afb504305bda3093b2a0e76c4:Matter)
RETURN collect(DISTINCT node_e62ce51afb504305bda3093b2a0e76c4) AS nodes_e62ce51afb504305bda3093b2a0e76c4
}

CALL {
WITH nodes_04fc99764ff440e2982ad556b0fb4355, nodes_aad6c4592a8b43ffb9adaf5084e0d72b
UNWIND nodes_04fc99764ff440e2982ad556b0fb4355 AS node_04fc99764ff440e2982ad556b0fb4355
UNWIND nodes_aad6c4592a8b43ffb9adaf5084e0d72b AS node_aad6c4592a8b43ffb9adaf5084e0d72b
MATCH path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b = (node_04fc99764ff440e2982ad556b0fb4355)-[:IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT*..3]->(node_aad6c4592a8b43ffb9adaf5084e0d72b)
WITH collect(DISTINCT path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b) AS path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b
RETURN path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b, [path IN path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b | [nodes(path)[0].uid, nodes(path)[-1].uid]] AS uids_path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b
}


CALL {
WITH nodes_aad6c4592a8b43ffb9adaf5084e0d72b, nodes_e62ce51afb504305bda3093b2a0e76c4
UNWIND nodes_aad6c4592a8b43ffb9adaf5084e0d72b AS node_aad6c4592a8b43ffb9adaf5084e0d72b
UNWIND nodes_e62ce51afb504305bda3093b2a0e76c4 AS node_e62ce51afb504305bda3093b2a0e76c4
MATCH path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4 = (node_aad6c4592a8b43ffb9adaf5084e0d72b)-[:IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT*..3]->(node_e62ce51afb504305bda3093b2a0e76c4)
WITH collect(DISTINCT path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4) AS path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4
RETURN path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4, [path IN path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4 | [nodes(path)[0].uid, nodes(path)[-1].uid]] AS uids_path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4
}

CALL {
WITH uids_path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b, uids_path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4
UNWIND range(0, size(uids_path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b)-1) AS idx0 UNWIND range(0, size(uids_path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4)-1) AS idx1
WITH *
  WHERE uids_path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4[idx1][0] = uids_path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b[idx0][-1]
RETURN collect(DISTINCT [idx0, idx1]) AS idxs
}

CALL {
WITH idxs, path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b, path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4
UNWIND idxs AS idx
RETURN apoc.coll.toSet(apoc.coll.flatten([nodes(path_04fc99764ff440e2982ad556b0fb4355_aad6c4592a8b43ffb9adaf5084e0d72b[idx[0]]), nodes(path_aad6c4592a8b43ffb9adaf5084e0d72b_e62ce51afb504305bda3093b2a0e76c4[idx[1]])])) AS pathNodes
}

WITH DISTINCT
  pathNodes,
  [NODE IN pathNodes | NODE.uid] + [x IN pathNodes | head([(x)-[:IS_A]->(neighbor) | neighbor.name])] AS combinations
UNWIND pathNodes AS pathNode
CALL apoc.case([
  pathNode:Matter,
  'OPTIONAL MATCH (onto)<-[:IS_A]-(pathNode)-[node_p:HAS_PROPERTY]->(property:Property)-[:IS_A]->(property_label:EMMOQuantity) RETURN DISTINCT [pathNode.uid, property.value, onto.name + "_" + property_label.name] as node_info',
  pathNode:Process,
  'OPTIONAL MATCH (onto)<-[:IS_A]-(pathNode)-[node_p:HAS_PARAMETER]->(property:Parameter)-[:IS_A]->(property_label:EMMOQuantity) RETURN DISTINCT [pathNode.uid, property.value, onto.name + "_" + property_label.name] as node_info'
])
YIELD value AS node_info
WITH DISTINCT collect(DISTINCT node_info['node_info']) AS node_info, combinations
RETURN DISTINCT apoc.coll.toSet(collect(DISTINCT combinations)) AS combinations,
                apoc.coll.toSet(apoc.coll.flatten(collect(DISTINCT node_info))) AS metadata

