# matGraph
A graph database, that leverages LLM's, deep embeddings and a standard representational frameworks (ontology), speeding up and semantically enriching materials science workflows for data storage and retrieval.

## Usage
Sandboxed version:

1. Clone Git repository
2. Rename .env.example to .env in root folder
3. Enter OpenAI API and Django Secret keys.
4. Build docker containers with `docker compose up -d --build`
5. After successfull build, wait for container `mg-frontend` to finish building the application (takes ~1min, you can check the installation status in `docker dashboard -> containers -> mg-frontend`).
6. Make sure all containers are running and access the app at `localhost:8000`
7. Enter any email address and password

## License
This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/legalcode). 
