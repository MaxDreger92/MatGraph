matGraph

matGraph is a graph database that leverages Large Language Models (LLMs), deep embeddings, and a standardized ontology to speed up and semantically enrich materials science workflows for data storage and retrieval. With native support for LangSmith, you can easily import shared datasets and integrate them into your own analysis pipelines.



Installation

Prerequisites

Before installing matGraph, ensure you have the following:

    Python Environment: Python 3.7 or later.

    OpenAI API Key:
    Sign up at OpenAI and retrieve your API key from your dashboard.

    LangChain API Key:
    Follow the LangChain documentation to obtain your API key.

    Neo4j:
    Install Neo4j for managing and visualizing your graph database. You can download the Community Edition from the Neo4j Download Center or install it via your package manager.

    For example, on Ubuntu:

    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
    echo 'deb https://debian.neo4j.com stable 4.4' | sudo tee /etc/apt/sources.list.d/neo4j.list
    sudo apt update
    sudo apt install neo4j

    For other operating systems, refer to the Neo4j Installation Guide.

Setting Up Environment Variables

After obtaining your API keys and installing Neo4j, set the following environment variables:

    export OPENAI_API_KEY='your-openai-api-key'
    export LANGCHAIN_API_KEY='your-langchain-api-key'

You can also place these in a .env file if you are using a package like python-dotenv.

Creating the .env File

A file named `env.example` is provided. This file should be filled in by the user with the necessary credentials and then renamed to `.env`. The file contains the following variables:

    # Django
    DJANGO_PORT=8000
    DJANGO_SECRET_KEY=

    # Postgres
    POSTGRES_USER=django_user
    POSTGRES_PASSWORD=
    POSTGRES_DB=django_db
    POSTGRES_HOST=mg-postgres

    # Neo4j
    NEOMODEL_NEO4J_BOLT_URL=

    # File Server
    FILESERVER_URL_POST=
    FILESERVER_URL_GET=
    FILESERVER_URL_DEL=
    FILE_SERVER_USER=
    FILE_SERVER_PASSWORD= 

    # OpenAI / Langchain
    OPENAI_API_KEY=
    LANGCHAIN_API_KEY=

Fill in the blank values with your specific credentials and configuration details, then rename the file from `env.example` to `.env`.

Installing Dependencies

Clone the repository and install the required dependencies:

    git clone https://github.com/yourusername/matGraph.git
    cd matGraph
    pip install -r requirements.txt

Running matGraph

Ensure that Neo4j is running, then start matGraph with:

    python app.py

File Server Setup

In addition to the main application, a file server is required to handle file operations. The file server must be constantly running and can be managed using NGINX as a reverse proxy.

Setting Up the File Server

1. Set Up the File Server Script

   Ensure that the file server script (e.g., `file_server.py`) is included in your project. This script should handle file operations such as POST, GET, and DELETE.

   Start the file server with:

        python file_server.py

   For continuous operation, consider using a process manager like `systemd`, `supervisord`, or `pm2`.

2. Install and Configure NGINX

   **Install NGINX:**

   For Ubuntu/Debian:

        sudo apt update
        sudo apt install nginx

   For other systems, refer to the [NGINX Installation Guide](https://nginx.org/en/docs/install.html).

   **Configure NGINX as a Reverse Proxy:**

   Create an NGINX configuration file (e.g., `/etc/nginx/sites-available/file_server`):

    ```nginx
    server {
        listen 80;
        server_name your_fileserver_domain.com;

        location / {
            proxy_pass http://127.0.0.1:YOUR_FILE_SERVER_PORT;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
    ```

   Replace `your_fileserver_domain.com` with your domain and `YOUR_FILE_SERVER_PORT` with the port on which your file server script is running.

   Enable the configuration:

        sudo ln -s /etc/nginx/sites-available/file_server /etc/nginx/sites-enabled/
        sudo nginx -t  # Test the configuration
        sudo systemctl restart nginx  # Restart NGINX to apply changes

3. Ensure Continuous Operation with systemd

   Create a service file at `/etc/systemd/system/file_server.service`:

    ```ini
    [Unit]
    Description=File Server
    After=network.target

    [Service]
    User=your_username
    WorkingDirectory=/path/to/your/project
    ExecStart=/usr/bin/python3 file_server.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

   Replace `your_username` and `/path/to/your/project` with your specific details, then run:

        sudo systemctl daemon-reload
        sudo systemctl enable file_server.service
        sudo systemctl start file_server.service

## Evaluate Pipeline

To evaluate the pipeline, ensure that you have completed the following steps:

1. **API Keys in .env:**  
   Make sure your `.env` file includes a valid `OPENAI_API_KEY` and `LANGCHAIN_API_KEY`.

2. **Install All Requirements:**  
   Ensure that all dependencies are installed by running:
   ```bash
   pip install -r requirements.txt

    Run Evaluations:
    Navigate to the importing/LLMEvaluation directory and execute the runevaluations.py script:

    cd importing/LLMEvaluation
    python runevaluations.py

This will trigger the evaluation pipeline, leveraging the provided API keys and dependencies to perform LLMEvaluation on the imported datasets.

Shared LangSmith Datasets

The shared datasets provided below are hosted on LangSmith and can be imported into your own LangSmith account. To do so:

    Access the Dataset: Click on the public link for the dataset.
    Import into LangSmith: In your LangSmith account, use the Import Dataset feature to add the dataset to your workspace.
    Utilize the Data: Once imported, the datasets can be used to run evaluations, track experiments, or integrate into your custom workflows.

Node Extraction Evaluation Datasets

    Property Dataset: https://smith.langchain.com/public/39078e2b-db6d-483d-b7d6-ba677334228b/d
    Parameter Dataset: https://smith.langchain.com/public/05aefa65-873f-4945-8ca5-dd0b65b30998/d
    Matter Dataset: https://smith.langchain.com/public/91045cc2-7c62-4395-bd55-9e21927e8ae4/d
    Manufacturing Dataset: https://smith.langchain.com/public/d3a20d4a-2551-4731-bf6a-315006b2b024/d
    Measurement Dataset: https://smith.langchain.com/public/50aa343a-92e2-4352-86ad-809f8da4ae26/d

Relationship Extraction Evaluation Datasets

    Has_Manufacturing Dataset: https://smith.langchain.com/public/4229b14a-da62-48c4-8c74-5dddc223b4ae/d
    Has_Measurement Dataset: https://smith.langchain.com/public/a9735b40-2dae-4e2c-8f06-ad29a8b6d9f9/d
    Has_Parameter Dataset: https://smith.langchain.com/public/f840de1a-a438-4eac-bc5a-a2987788a5f5/d
    Has_Property Dataset: https://smith.langchain.com/public/8957cd02-3e81-469d-9f93-75d0f993552d/d
    Has_Metadata Dataset: https://smith.langchain.com/public/888d221a-de63-42a2-8236-14a60858f6c9/d

Usage

Access matGraph as a web application at: https://matgraph.xyz

License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.
