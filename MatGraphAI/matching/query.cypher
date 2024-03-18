MATCH (onto_fa2c1dfbd0d045108fe66e0d24d36acc:EMMOProcess {uid: 'd4b87963f1d449b6b3c1d17fb96393f0'}),
      (onto_fbe4c2d5e1624da99734f598baaff42f:EMMOMatter {uid: 'eea92a0d8b054d55b1894ce172ab1aa4'}),
      (onto_18c98ecd3b664db9a7ff7d054eb59f0b:EMMOMatter {uid: '18299d51bf0340a3823c6f6d99e945ec'}),
      (onto_9499ee59683841b9ac9326c09c93fb04:EMMOQuantity {uid: '4bf3c3677bd14d9683013cb0f2b28953'})
CALL {
WITH onto_fa2c1dfbd0d045108fe66e0d24d36acc
OPTIONAL MATCH (onto_fa2c1dfbd0d045108fe66e0d24d36acc)<-[:EMMO__IS_A*..]-(tree_onto_fa2c1dfbd0d045108fe66e0d24d36acc:EMMOProcess)
RETURN collect(DISTINCT tree_onto_fa2c1dfbd0d045108fe66e0d24d36acc) + collect(DISTINCT onto_fa2c1dfbd0d045108fe66e0d24d36acc) AS combined_fa2c1dfbd0d045108fe66e0d24d36acc
}
CALL {
WITH onto_fbe4c2d5e1624da99734f598baaff42f
OPtIONAL MATCH (onto_fbe4c2d5e1624da99734f598baaff42f)<-[:EMMO__IS_A*..]-(tree_onto_fbe4c2d5e1624da99734f598baaff42f:EMMOMatter)
RETURN collect(DISTINCT tree_onto_fbe4c2d5e1624da99734f598baaff42f) + collect(DISTINCT onto_fbe4c2d5e1624da99734f598baaff42f) AS combined_fbe4c2d5e1624da99734f598baaff42f
}

CALL
{
WITH onto_18c98ecd3b664db9a7ff7d054eb59f0b
OPTIONAL MATCH (onto_18c98ecd3b664db9a7ff7d054eb59f0b)<-[:EMMO__IS_A*..]-(tree_onto_18c98ecd3b664db9a7ff7d054eb59f0b:EMMOMatter)
RETURN collect(DISTINCT tree_onto_18c98ecd3b664db9a7ff7d054eb59f0b) + collect(DISTINCT onto_18c98ecd3b664db9a7ff7d054eb59f0b) AS combined_18c98ecd3b664db9a7ff7d054eb59f0b
}

CALL
{
WITH onto_9499ee59683841b9ac9326c09c93fb04
OPTIONAL MATCH (onto_9499ee59683841b9ac9326c09c93fb04)<-[:EMMO__IS_A*..]-(tree_onto_9499ee59683841b9ac9326c09c93fb04:EMMOQuantity)
RETURN collect(DISTINCT tree_onto_9499ee59683841b9ac9326c09c93fb04) + collect(DISTINCT onto_9499ee59683841b9ac9326c09c93fb04) AS combined_9499ee59683841b9ac9326c09c93fb04
}

CALL {
WITH combined_fa2c1dfbd0d045108fe66e0d24d36acc
UNWIND combined_fa2c1dfbd0d045108fe66e0d24d36acc AS full_onto_fa2c1dfbd0d045108fe66e0d24d36acc
MATCH (full_onto_fa2c1dfbd0d045108fe66e0d24d36acc)<-[:IS_A]-(node_fa2c1dfbd0d045108fe66e0d24d36acc:Manufacturing)
RETURN collect( DISTINCT node_fa2c1dfbd0d045108fe66e0d24d36acc) AS nodes_fa2c1dfbd0d045108fe66e0d24d36acc
}

CALL {
WITH combined_fbe4c2d5e1624da99734f598baaff42f
UNWIND combined_fbe4c2d5e1624da99734f598baaff42f AS full_onto_fbe4c2d5e1624da99734f598baaff42f
MATCH (full_onto_fbe4c2d5e1624da99734f598baaff42f)<-[:IS_A]-(node_fbe4c2d5e1624da99734f598baaff42f:Matter)
RETURN collect( DISTINCT node_fbe4c2d5e1624da99734f598baaff42f) AS nodes_fbe4c2d5e1624da99734f598baaff42f
}

CALL {
WITH combined_18c98ecd3b664db9a7ff7d054eb59f0b
UNWIND combined_18c98ecd3b664db9a7ff7d054eb59f0b AS full_onto_18c98ecd3b664db9a7ff7d054eb59f0b
MATCH (full_onto_18c98ecd3b664db9a7ff7d054eb59f0b)<-[:IS_A]-(node_18c98ecd3b664db9a7ff7d054eb59f0b:Matter)
RETURN collect( DISTINCT node_18c98ecd3b664db9a7ff7d054eb59f0b) AS nodes_18c98ecd3b664db9a7ff7d054eb59f0b
}

CALL {
WITH combined_9499ee59683841b9ac9326c09c93fb04
UNWIND combined_9499ee59683841b9ac9326c09c93fb04 AS full_onto_9499ee59683841b9ac9326c09c93fb04
MATCH (full_onto_9499ee59683841b9ac9326c09c93fb04)<-[:IS_A]-(node_9499ee59683841b9ac9326c09c93fb04:Parameter)
RETURN collect( DISTINCT node_9499ee59683841b9ac9326c09c93fb04) AS nodes_9499ee59683841b9ac9326c09c93fb04
}


CALL {
WITH nodes_fa2c1dfbd0d045108fe66e0d24d36acc, nodes_fbe4c2d5e1624da99734f598baaff42f
UNWIND nodes_fa2c1dfbd0d045108fe66e0d24d36acc AS node_fa2c1dfbd0d045108fe66e0d24d36acc
UNWIND nodes_fbe4c2d5e1624da99734f598baaff42f AS node_fbe4c2d5e1624da99734f598baaff42f
MATCH path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f = (node_fa2c1dfbd0d045108fe66e0d24d36acc)-[:IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT*..3]->(node_fbe4c2d5e1624da99734f598baaff42f:Matter|Manufacturing)
WITH collect(DISTINCT path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f) AS path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f
RETURN path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f, [path IN path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f | [nodes(path)[0].uid, nodes(path)[-1].uid]] AS uids_path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f
}

CALL {
WITH nodes_18c98ecd3b664db9a7ff7d054eb59f0b, nodes_fa2c1dfbd0d045108fe66e0d24d36acc
UNWIND nodes_18c98ecd3b664db9a7ff7d054eb59f0b AS node_18c98ecd3b664db9a7ff7d054eb59f0b
UNWIND nodes_fa2c1dfbd0d045108fe66e0d24d36acc AS node_fa2c1dfbd0d045108fe66e0d24d36acc
MATCH path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc = (node_18c98ecd3b664db9a7ff7d054eb59f0b)-[:IS_MANUFACTURING_INPUT|IS_MANUFACTURING_OUTPUT*..3]->(node_fa2c1dfbd0d045108fe66e0d24d36acc)
WITH collect(DISTINCT path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc) AS path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc
RETURN path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc, [path IN path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc | [nodes(path)[0].uid, nodes(path)[-1].uid]] AS uids_path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc
}

CALL {
WITH nodes_fa2c1dfbd0d045108fe66e0d24d36acc, nodes_9499ee59683841b9ac9326c09c93fb04
UNWIND nodes_fa2c1dfbd0d045108fe66e0d24d36acc AS node_fa2c1dfbd0d045108fe66e0d24d36acc
UNWIND nodes_9499ee59683841b9ac9326c09c93fb04 AS node_9499ee59683841b9ac9326c09c93fb04
MATCH path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04 = (node_fa2c1dfbd0d045108fe66e0d24d36acc)-[:HAS_PARAMETER*..3]->(node_9499ee59683841b9ac9326c09c93fb04:Parameter|Quantity)
WITH collect(DISTINCT path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04) AS path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04
RETURN path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04, [path IN path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04 | [nodes(path)[0].uid, nodes(path)[-1].uid]] AS uids_path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04
}

CALL {
WITH uids_path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f, uids_path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc, uids_path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04
UNWIND range(0, size(uids_path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f)-1) AS idx1
UNWIND range(0, size(uids_path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc)-1) AS idx2
UNWIND range(0, size(uids_path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04)-1) AS idx3
WITH idx1, idx2, idx3, uids_path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f, uids_path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc, uids_path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04
WHERE
  uids_path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f[idx1][0] = uids_path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc[idx2][1]
AND
uids_path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc[idx2][1] = uids_path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04[idx3][0]
RETURN collect(DISTINCT [idx1, idx2, idx3]) AS idxs
}

CALL {
WITH idxs, path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f, path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc, path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04
UNWIND idxs as indeces
WITH apoc.coll.toSet(apoc.coll.flatten([nodes(path_fa2c1dfbd0d045108fe66e0d24d36acc_fbe4c2d5e1624da99734f598baaff42f[indeces[0]]), nodes(path_18c98ecd3b664db9a7ff7d054eb59f0b_fa2c1dfbd0d045108fe66e0d24d36acc[indeces[1]]), nodes(path_fa2c1dfbd0d045108fe66e0d24d36acc_9499ee59683841b9ac9326c09c93fb04[indeces[2]])]))
AS pathNodes
RETURN pathNodes
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