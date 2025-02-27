# MatGraph

**MatGraph** is a cutting-edge graph database that leverages Large Language Models (LLMs), deep embeddings, and a standardized ontology to accelerate and semantically enrich materials science workflows for data storage and retrieval. With native support for LangSmith, you can easily import shared datasets and integrate them into your own analysis pipelines.

---

## Table of Contents

- [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Environment Setup](#environment-setup)
   - [Clone & Install Python Dependencies](#clone--install-python-dependencies)
- [Backend Setup](#backend-setup)
   - [Backend Prerequisites](#backend-prerequisites)
   - [Installation & Setup](#installation--setup)
- [Frontend Setup](#frontend-setup)
   - [Prerequisites](#frontend-prerequisites)
   - [Installation & Setup](#frontend-installation--setup)
- [File Server Setup](#file-server-setup)
   - [Setting Up the File Server](#setting-up-the-file-server)
   - [Configuring NGINX as a Reverse Proxy](#configuring-nginx-as-a-reverse-proxy)
   - [Ensuring Continuous Operation with systemd](#ensuring-continuous-operation-with-systemd)
- [Evaluate Pipeline](#evaluate-pipeline)
- [Shared LangSmith Datasets](#shared-langsmith-datasets)
   - [Node Extraction Evaluation Datasets](#node-extraction-evaluation-datasets)
   - [Relationship Extraction Evaluation Datasets](#relationship-extraction-evaluation-datasets)
- [Usage](#usage)
- [License](#license)

---

## Installation

### Prerequisites

Before you begin, ensure you have the following installed and configured:

- **Python Environment:** Python 3.7 or later.
- **OpenAI API Key:** Sign up at [OpenAI](https://openai.com/) and retrieve your API key from your dashboard.
- **LangChain API Key:** Follow the [LangChain documentation](https://python.langchain.com/) to obtain your API key.
- **Neo4j:**  
  Install Neo4j for managing and visualizing your graph database.  
  **Ubuntu Example:**
  ```bash
  wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
  echo 'deb https://debian.neo4j.com stable 4.4' | sudo tee /etc/apt/sources.list.d/neo4j.list
  sudo apt update
  sudo apt install neo4j

For other operating systems, refer to the Neo4j Installation Guide.
### Environment Setup

    API Keys and Configuration:

    Set the following environment variables:

export OPENAI_API_KEY='your-openai-api-key'
export LANGCHAIN_API_KEY='your-langchain-api-key'

Creating the .env File:

A sample file named env.example is provided. Populate this file with your credentials and configuration details, then rename it to .env:

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

### Clone & Install Python Dependencies

Clone the repository and install the required Python dependencies:

git clone https://github.com/MaxDreger92/MatGraph.git
cd MatGraph
pip install -r requirements.txt

##Backend Setup

The backend, housed in the UserBackendNodeJS directory, provides the API and server-side logic.
### Backend Prerequisites

    Node.js and npm: Ensure that Node.js (which includes npm) is installed. Check your installation:

    node -v
    npm -v

### Installation & Setup

    Navigate to the Backend Directory:

cd UserBackendNodeJS

Install Dependencies:

npm install

Starting the Backend Server:

Depending on your setup, start the server using:

npm start

or, if using a tool like nodemon for automatic restarts:

    nodemon index.js

    The backend is typically accessible at http://localhost:5000 (or your configured port).

    Additional Notes:
        If the backend requires environment-specific configurations, create an .env file in the UserBackendNodeJS directory.
        Check the scripts section in the package.json for other available commands.

Frontend Setup

The frontend is a React application that interacts with the backend.
Frontend Prerequisites

    Node.js and npm: Ensure you have Node.js installed. Verify your installation:

    node -v
    npm -v

### Installation & Setup

    Navigate to the Frontend Directory:

cd frontend

Install Dependencies:

npm install

Starting the Frontend Application:

Start the development server with:

    npm start

    The React app will run on http://localhost:3000 and auto-reloads upon changes.

## File Server Setup

A dedicated file server is required to handle file operations (POST, GET, DELETE) and should run continuously.
### Setting Up the File Server

    Prepare the File Server Script:

    Ensure that file_server.py (or your designated file server script) is included in your project.

    Run the File Server:

    Start the file server by executing:

    python file_server.py

    For continuous operation, consider using a process manager such as systemd, supervisord, or pm2.

### Configuring NGINX as a Reverse Proxy

    Install NGINX:

    On Ubuntu/Debian:

sudo apt update
sudo apt install nginx

For other systems, refer to the NGINX Installation Guide.

Configure NGINX:

Create a configuration file (e.g., /etc/nginx/sites-available/file_server):

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

Replace your_fileserver_domain.com with your domain and YOUR_FILE_SERVER_PORT with the port your file server is using.

Enable and Test NGINX Configuration:

    sudo ln -s /etc/nginx/sites-available/file_server /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx

### Ensuring Continuous Operation with systemd

Create a service file at /etc/systemd/system/file_server.service:

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

Replace your_username and /path/to/your/project with your specific details, then run:

sudo systemctl daemon-reload
sudo systemctl enable file_server.service
sudo systemctl start file_server.service

### Evaluate Pipeline

Evaluating the pipeline does not require a frontend or backend setup. All that is needed is the installation of all 
Python requirements, the creation of a LangSmith and OpenAI API key. The evaulation can be used to check the pipelines 
accuracy on the given data sets. Additionally, more datasets can be added. The evaluation can be done for each step of the 
pipeline separately. 
The evaluation of the pipeline, as it is separated by steps does not contain the raw tables, it contains the langsmith 
dataset which consist of JSON objects, that contain the tables as well as additional information and context, depending
on the step and dataset.

The raw tables as well as the artificial datasets for the validation of the node type and relationship type extraction
can be found in the data_set directory.

To verify that the complete pipeline is working correctly:

    Confirm API Keys in .env:

    Ensure your .env file includes valid OPENAI_API_KEY and LANGCHAIN_API_KEY.

    Install All Python Requirements:

pip install -r requirements.txt

Run Evaluations:

Navigate to the importing/LLMEvaluation directory and run:

    cd importing/LLMEvaluation
    python runevaluations.py

    This script leverages your API keys and dependencies to perform LLMEvaluation on the imported datasets.

## Shared LangSmith Datasets

MatGraph integrates with LangSmith to import and utilize shared datasets. These datasets are available for various evaluation tasks.
### Node Extraction Evaluation Datasets

    Property Dataset: https://smith.langchain.com/public/39078e2b-db6d-483d-b7d6-ba677334228b/d
    Parameter Dataset: https://smith.langchain.com/public/05aefa65-873f-4945-8ca5-dd0b65b30998/d
    Matter Dataset: https://smith.langchain.com/public/91045cc2-7c62-4395-bf6a-315006b2b024/d
    Manufacturing Dataset: https://smith.langchain.com/public/d3a20d4a-2551-4731-bf6a-315006b2b024/d
    Measurement Dataset: https://smith.langchain.com/public/50aa343a-92e2-4352-86ad-809f8da4ae26/d

### Relationship Extraction Evaluation Datasets

    Has_Manufacturing Dataset: https://smith.langchain.com/public/4229b14a-da62-48c4-8c74-5dddc223b4ae/d
    Has_Measurement Dataset: https://smith.langchain.com/public/a9735b40-2dae-4e2c-8f06-ad29a8b6d9f9/d
    Has_Parameter Dataset: https://smith.langchain.com/public/f840de1a-a438-4eac-bc5a-a2987788a5f5/d
    Has_Property Dataset: https://smith.langchain.com/public/8957cd02-3e81-469d-9f93-75d0f993552d/d
    Has_Metadata Dataset: https://smith.langchain.com/public/888d221a-de63-42a2-8236-14a60858f6c9/d

Usage

Access the MatGraph web application at: https://matgraph.xyz
License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.

