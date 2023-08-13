from mat2devplatform.matgraph.useful_queries import *
from neomodel import db


def upload_query(query):
    db.cypher_query(query)


if __name__ == "__main__":
    upload_query()