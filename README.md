matGraph

matGraph is a graph database that leverages Large Language Models (LLMs), deep embeddings, and a standardized ontology to speed up and semantically enrich materials science workflows for data storage and retrieval. With native support for LangSmith, you can easily import shared datasets and integrate them into your own analysis pipelines.
Importing Shared Datasets into LangSmith

The shared datasets provided below are hosted on LangSmith and can be imported into your own LangSmith account. To do so:

    Access the Dataset: Click on the public link for the dataset.
    Import into LangSmith: In your LangSmith account, use the Import Dataset feature to add the dataset to your workspace.
    Utilize the Data: Once imported, the datasets can be used to run evaluations, track experiments, or integrate into your custom workflows.

Node Extraction Evaluation Datasets

    Property Dataset: Download
    Parameter Dataset: Download
    Matter Dataset: Download
    Manufacturing Dataset: Download
    Measurement Dataset: Download

Relationship Extraction Evaluation Datasets

    Has_Manufacturing Dataset: Download
    Has_Measurement Dataset: Download
    Has_Parameter Dataset: Download
    Has_Property Dataset: Download
    Has_Metadata Dataset: Download

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
Installing Dependencies

Clone the repository and install the required dependencies:

git clone https://github.com/yourusername/matGraph.git
cd matGraph
pip install -r requirements.txt

Running matGraph

Ensure that Neo4j is running, then start matGraph with:

python app.py

Reproducing and Accessing Evaluation Results

The shared datasets provided above are used for node and relationship extraction evaluations. Once you import these datasets into your LangSmith account (see the Importing Shared Datasets section), you can run evaluations, track experiment metrics, and visualize results through the matGraph interface.
Usage

Access matGraph as a web application at: https://matgraph.xyz
License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.