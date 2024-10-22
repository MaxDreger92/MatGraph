# Matching
API module providing semantic search functionality, comprising the following endpoints:

## fabrication-workflow
-   Construct database query from client submitted node graph
-   Execute processing of constructed query
-   Return query results to client

### URI
`/api/match/fabrication-workflow`

### Method
`POST`

### Headers
-   `Content-Type: multipart/form-data`
-   `HTTP_API_KEY: your_api_key_here`

### Request Body (form-data)
-   `graph` - a json string containing two lists, `nodes` and `relationships`:

```json
{
    "nodes": [
        {
            "id": "UNIQUE_IDENTIFIER",
            "name": {
                "value": "NODE_NAME"
            },
            "label": "NODE_LABEL",
            "attributes": {
                "name": {
                    "value": "NODE_NAME"
                },
                "value": {
                    "value": "VALUE",
                    "operator": "OPERATOR"
                },
                "batch_num": {
                    "value": "VALUE",
                },
                "ratio": {
                    "value": "VALUE",
                    "operator": "OPERATOR"
                },
                "concentration": {
                    "value": "VALUE",
                    "operator": "OPERATOR"
                },
                "unit": {
                    "value": "VALUE",
                },
                "std": {
                    "value": "VALUE",
                    "operator": "OPERATOR"
                },
                "error": {
                    "value": "VALUE",
                    "operator": "OPERATOR"
                },
                "identifier": {
                    "value": "VALUE",
                },
            }
        }, ...
    ],
    "relationships": [
        {
            "rel_type": "RELATIONSHIP_TYPE",
            "connection": [
                "START_NODE_ID",
                "END_NODE_ID"
            ]
        }, ...
    ]
}
```

Nodes must have the following entries:

-   <b>id</b>
    -   unique node identifier
    -   must be unique only for any given graph, not outside of the graph (e.g. numbering from 0 to n-1, for n nodes)
-   <b>name</b>
    -   arbitrary given name, will be compared for similarity with other node names
-   <b>label</b>
    -   relates to ontology classes, currently the following:<br>
        -   'matter'<br>
        -   'measurement'<br>
        -   'manufacturing'<br>
        -   'property'<br>
        -   'metadata'<br>
        -   'parameter'<br>
        -   'simulation'<br>

For node attributes, only the `name` attribute is mandatory. The list of possible optional attributes depends on the node label:

-   <b>matter</b>
    -   identifier, batch_num, ratio, concentration
-   <b>property, parameter</b>
    -   value, unit, std, error
-   <b>manufacturing, measurement, metadata</b>
    -   identifier

Attributes have a stringified `value` field and may also have an additional `operator`. Valid operators are:

-   '<'
-   '<='
-   '='
-   '!='
-   '>='
-   '>'

Relationships must have a `rel_type`, aswell as a `connection` comprising of a starting and an end node id. Valid relationship types are (from-to):

-   <b>matter-manufacturing</b>
    -   'IS_MANUFACTURING_INPUT'
-   <b>manufacturing-matter</b>
    -   'IS_MANUFACTURING_OUTPUT'
-   <b>matter-measurement</b>
    -   'IS_MEASUREMENT_INPUT'
-   <b>matter-property</b>
    -   'HAS_PROPERTY'
-   <b>manufacturing-parameter</b>
    -   'HAS_PARAMETER'
-   <b>measurement-parameter</b>
    -   'HAS_PARAMETER'
-   <b>measurement-property</b>
    -   'HAS_MEASUREMENT_OUTPUT'
-   <b>manufacturing-metadata</b>
    -   'HAS_METADATA'
-   <b>measurement-metadata</b>
    -   'HAS_METADATA'
-   <b>matter-matter</b>
    -   'HAS_PART'
-   <b>manufacturing-manufacturing</b>
    -   'HAS_PART'
-   <b>measurement-measurement</b>
    -   'HAS_PART'

### Response
- CSV