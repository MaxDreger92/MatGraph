## Matching
The matching module is an API module providing semantic search functionality, comprising the following endpoints:

### match/fabrication-workflow/
- Construct database query from user-submitted node graph
- Execute processing of constructed query
- Return query results to user

<h4><span style="color:#3388cc">class </span><span style="color:#00bbaa">FabricationWorkflowMatcher</span></h4>

This Matcher class is the primary class responsible for matching the user-submitted workflow with database entries.

Methods:

1. <span style="color:#ffdd77">\_\_init__</span>

   - **Purpose**: Initializes the Matcher instance with given workflow data.
   - **Functionality**:
     - Parses the workflow nodes and maps each node to its corresponding UID based on its label using the **'ONTOMAPPER'** dictionary.
     - Initializes the relationships between the nodes.
     - Calls the superclass **('Matcher')** constructor.
   - **Parameters**:
     - **workflow_list**: A dictionary containing the workflow nodes and relationships.
     - **count**: A boolean indicating whether to count the results.
     - **kwargs**: Additional keyword arguments for the superclass

2. <span style="color:#ffdd77">build\_query</span>

   - **Purpose**: Constructs a comprehensive Cypher query to match the workflow against the database.
   - **Functionality**:
     - Constructs ontology queries for each node using **'\_build\_ontology\_query'**.
     - Constructs tree queries for each node using **'\_build\_tree\_query'**.
     - Constructs find nodes queries to locate specific nodes using **'\_build\_find\_nodes\_query'**.
     - Constructs path queries and conditions to match the relationships between nodes using **'\_build\_path\_queries\_and\_conditions'**.
     - Assembles all parts into a final query string.
   - **Returns**: A tuple containing the final query string and an empty dictionary (for potential query parameters).

3. <span style="color:#ffdd77">\_build\_ontology\_query</span>

   - **Purpose**: Builds a Cypher query for an ontology node.
   - **Functionality**: Maps the node's UID and label to its ontology representation.
   - **Parameters**: **node** - The workflow node.
   - **Returns**: A Cypher query string for the ontology node.

4. <span style="color:#ffdd77">\_build\_tree\_query</span>

   - **Purpose**: Builds a Cypher query to retrieve all nodes in the ontology tree.
   - **Functionality**: Uses the **'IS_A'** relationship to find all related ontology nodes.
   - **Parameters**:
     - **node_id**: The node's unique identifier.
     - **label**: The node's label.
   - **Returns**: A Cypher query string to fetch ontology tree nodes.

5. <span style="color:#ffdd77">\_build\_find\_nodes\_query</span>

   - **Purpose**: Builds a Cypher query to find specific nodes based on their attributes.
   - **Functionality**: Depending on the label, constructs queries to match nodes with given attributes and conditions.
   - **Parameters**:
     - **node_id**: The node's unique identifier.
     - **label**: The node's label.
     - **attributes**: The node's attributes.
   - **Returns**: A Cypher query string to find nodes with specific attributes.

6. <span style="color:#ffdd77">\_build\_path\_queries</span>

   - **Purpose**: Builds Cypher queries for the paths (relationships) between nodes.
   - **Functionality**: Iterates through relationships and constructs queries to match the paths using **'\_build\_single\_path\_query'**.
   - **Returns**: A list of Cypher query strings for the paths.

7. <span style="color:#ffdd77">\_build\_path\_conditions</span>

   - **Purpose**: Builds conditions and connectors for the path queries.
   - **Functionality**: Generates conditions to ensure the paths are connected correctly and constructs a combined query for path matching.
   - **Parameters**:
     - **paths**: List of path query variables.
     - **uid_paths**: List of UID path query variables.
     - **xid_paths**: List of index path query variables.
     - **relationships**: List of relationships between nodes.
   - **Returns**: A Cypher query string for path conditions.

8. <span style="color:#ffdd77">\_build\_single\_path\_query</span>

   - **Purpose**: Builds a Cypher query for a single path between two nodes.
   - **Functionality**: Matches nodes connected by the specified relationship type.
   - **Parameters**:
     - **source**: Source node identifier.
     - **target**: Target node identifier.
     - **rel_type**: Type of relationship between the nodes.
     - **index**: Index of the path query.
   - **Returns**: A Cypher query string for the single path.

9. <span style="color:#ffdd77">\_build\_path\_queries\_and\_conditions</span>

   - **Purpose**: Combines all path queries and conditions into a single query string.
   - **Functionality**: Calls **'\_build\_path\_queries'** and **'\_build\_path\_conditions'** to create the full query segment for path matching.
   - **Returns**: A combined Cypher query string for paths and conditions.

10. <span style="color:#ffdd77">\_build\_results</span>

    - **Purpose**: Builds the final part of the Cypher query to retrieve the results.
    - **Functionality**: Aggregates and processes the matched nodes and their properties.
    - **Returns**: A Cypher query string for fetching results.

11. <span style="color:#ffdd77">build\_result</span>

    - **Purpose**: Processes the query results into a structured format.
    - **Functionality**: Uses **'create_table_structure'** to convert the raw query results into a DataFrame.
    - **Returns**: A DataFrame containing the structured results.

12. <span style="color:#ffdd77">build\_results\_for\_report</span>

    - **Purpose**: Prepares the results for reporting.
    - **Functionality**: Calls **'create_table_structure'** to process the results and returns them in a list format suitable for reports.
    - **Returns**: A list of result values and columns.

<h4><span style="color:#3388cc">def </span><span style="color:#ffdd77">create_table_structure</span></h4>