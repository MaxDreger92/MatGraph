# Importing
API module providing data ingestion functionality, comprising the following endpoints:

## label-extract
- Handle storage of user data file
- Create `ImportProcess`
- Submit task `extract_labels` to task manager
- Return `process_id` and `status`

### URI
`/api/import/label-extract/?user_id=your_user_id_here`

### Method
`POST`

### Headers
-   `Content-Type`: `multipart/form-data`
-   `HTTP_API_KEY`: `your_api_key_here`

### Request Body (form-data)
- `file` - CSV Dataset
- `context` - `String`

### Response
- HTTP status code: `201`
- `process_id` - `String`
- `status` - `String`


## attribute-extract
- Retrieve `ImportProcess`
- Retrieve `labels` from either request data or the process object
- Submit task `extract_attributes` to task manager
- Return `status`

### URI
`/api/import/attribute-extract/?user_id=your_user_id_here&process_id=your_process_id_here`

### Method
`POST`

### Headers
-   `Content-Type`: `multipart/form-data`
-   `HTTP_API_KEY`: `your_api_key_here`

### Request Body (form-data)
- `labels` - Dictionary (optional)

### Response
- HTTP status code: `200`
- `status` - `String`


## node-extract
- Retrieve `ImportProcess`
- Retrieve `attributes` from either request data or the process object
- Submit task `extract_nodes` to task manager
- Return `status`

### URI
`/api/import/node-extract/?user_id=your_user_id_here&process_id=your_process_id_here`

### Method
`POST`

### Headers
-   `Content-Type`: `multipart/form-data`
-   `HTTP_API_KEY`: `your_api_key_here`

### Request Body (form-data)
- `attributes` - Dictionary (optional)

### Response
- HTTP status code: `200`
- `status` - `String`


## graph-extract
- Retrieve `ImportProcess`
- Retrieve nodes as `graph` from either request data or the process object
- Submit task `extract_relationships` to task manager
- Return `status`

### URI
`/api/import/graph-extract/?user_id=your_user_id_here&process_id=your_process_id_here`

### Method
`POST`

### Headers
-   `Content-Type`: `multipart/form-data`
-   `HTTP_API_KEY`: `your_api_key_here`

### Request Body (form-data)
- `graph` - JSON String (optional)

### Response
- HTTP status code: `200`
- `status` - `String`


## graph-import
- Retrieve `ImportProcess`
- Retrieve `graph` from either request data or the process object
- Submit task `import_graph` to task manager
- Return `status`

### URI
`/api/import/graph-import/?user_id=your_user_id_here&process_id=your_process_id_here`

### Method
`POST`

### Headers
-   `Content-Type`: `multipart/form-data`
-   `HTTP_API_KEY`: `your_api_key_here`

### Request Body (form-data)
- `graph` - JSON String (optional)

### Response
- HTTP status code: `200`
- `status` - `String`


## process-cancel
- Retrieve `ImportProcess`
- Attempt cancelling task
- Return `status`

### URI
`api/import/cancel/?user_id=your_user_id_here&process_id=your_process_id_here`

### Method
`PATCH`

### Headers
-   `Content-Type`: `multipart/form-data`
-   `HTTP_API_KEY`: `your_api_key_here`

### Response
- HTTP status code: `200`
- `status` - `String`


## process-report
- Retrieve `ImportProcess`
- Validate `key`
- Attempt retrieve process report data
- Return `status` and data as `key` if possible

### URI
`/api/import/report/?user_id=your_user_id_here&process_id=your_process_id_here&key=your_key_here`

### Method
`GET`

### Headers
-   `HTTP_API_KEY`: `your_api_key_here`

### Response
- HTTP status code: `200`
- `status` - `String`
- `key` - Requested Data


## process-delete
- Retrieve `ImportProcess`
- Delete process
- Return `status`

### URI
`/api/import/delete/?user_id=your_user_id_here&process_id=your_process_id_here`

### Method
`DELETE`

### Headers
-   `HTTP_API_KEY`: `your_api_key_here`

### Response
- HTTP status code: `200`
- `status` - `String`