## Importing
The importing module is an API module, providing the data ingestion functionality, comprising the following endpoints:

### label-extract
- Handle storage of user data file
- Extract node labels from data file
- Return node labels to user for manual revision

### attribute-extract
- Extract node attributes from data file for revised node labels
- Return node attributes to user for manual revision

### node-extract
- Combine extracted labels and attributes into node entities
- Return nodes to user for manual revision

### graph-extract
- Construct relationships between nodes
- Return node graph to user for final revision and confirmation

### graph-import
- Embed node identifiers (node names)
- Map embeddings to ontology
- Store graph in database
