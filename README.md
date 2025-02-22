# matGraph

**matGraph** is a cutting-edge graph database that leverages Large Language Models (LLMs), deep embeddings, and a standardized ontology to accelerate and semantically enrich materials science workflows for data storage and retrieval. With native support for LangSmith, you can easily import shared datasets and integrate them into your own analysis pipelines.

---

## Table of Contents

- [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Environment Setup](#environment-setup)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [File Server Setup](#file-server-setup)
- [Evaluate Pipeline](#evaluate-pipeline)
- [Shared LangSmith Datasets](#shared-langsmith-datasets)
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
Environment Setup

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

Clone and Install Python Dependencies:

    git clone https://github.com/yourusername/matGraph.git
    cd matGraph
    pip install -r requirements.txt

Backend Setup

The backend, housed in the UserBackendNodeJS directory, provides the API and server-side logic.
Prerequisites

    Node.js and npm: Ensure that Node.js (which includes npm) is installed. Check your installation:

    node -v
    npm -v

Installation & Setup

    Navigate to the Backend Directory:

cd UserBackendNodeJS

Install Dependencies:

npm install

Starting the Backend Server:

npm start

or, if using nodemon for automatic restarts:

    nodemon index.js

    The backend is typically accessible at http://localhost:5000 (or your configured port).

Frontend Setup

The frontend is a React application that interacts with the backend.
Prerequisites

    Node.js and npm: Ensure you have Node.js installed. Verify your installation:

    node -v
    npm -v

Installation & Setup

    Navigate to the Frontend Directory:

cd frontend

Install Dependencies:

npm install

Starting the Frontend Application:

    npm start

    The React app will run on http://localhost:3000 and auto-reloads upon changes.

File Server Setup

A dedicated file server is required to handle file operations (POST, GET, DELETE) and should run continuously.
Running the File Server

    Start the File Server:

python file_server.py

Ensure Continuous Operation with systemd

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

Evaluate Pipeline

To verify that the complete pipeline is working correctly:

    Confirm API Keys in .env:

pip install -r requirements.txt

Run Evaluations:

    cd importing/LLMEvaluation
    python runevaluations.py

Shared LangSmith Datasets

matGraph integrates with LangSmith to import and utilize shared datasets. These datasets are available for various evaluation tasks:
Node Extraction Evaluation Datasets

    Property Dataset
    Parameter Dataset
    Matter Dataset
    Manufacturing Dataset
    Measurement Dataset

Relationship Extraction Evaluation Datasets

    Has_Manufacturing Dataset
    Has_Measurement Dataset
    Has_Parameter Dataset
    Has_Property Dataset
    Has_Metadata Dataset

Usage

Access the matGraph web application at: https://matgraph.xyz
License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.


This is a properly formatted `README.md` file with clear headings,