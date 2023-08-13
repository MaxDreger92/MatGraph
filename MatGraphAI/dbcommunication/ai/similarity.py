# similarity calculation
import time

import faiss
import numpy as np
from neomodel import db

from skills.ai.config import EMBEDDING_DIMENSIONS

MAX_VALUE = 1.0
OVERALL_THRESHOLD = 0.85
INITIAL_CALCULATION = 400 # how many similarities to calculate per skill (before applying thresholds)
CHUNK_SIZE = 30000  # db write, before filtering


def scale(similarity):
    return 0 if similarity < OVERALL_THRESHOLD else min(
        (similarity-OVERALL_THRESHOLD) * (1/(MAX_VALUE-OVERALL_THRESHOLD)),
        MAX_VALUE
    )

def ingest(similarities):

    db.cypher_query('''
        UNWIND $similarities as similarity
        MATCH
          (skill1:Skill {uid: similarity[0]}),
          (skill2:Skill {uid: similarity[1]})
        CREATE
          (skill1)-[rel:SIMILAR {similarity: similarity[2]}]->(skill2)
    ''', {
        'similarities': similarities
    })

def update_similarities(cmd):

    cmd.stdout.write('fetching embeddings...')

    results, meta = db.cypher_query('''
        MATCH (skill:Skill)<-[:FOR]-(emb:ModelEmbedding)
        RETURN skill.uid as uid, emb.vector as vector
    ''')

    cmd.stdout.write('converting to np arrays')
    embeddings = np.array([
        np.array(row[1]) for row in results
    ])


    print('creating vector index...', end='')
    index = faiss.IndexFlatIP(EMBEDDING_DIMENSIONS)
    index.add(embeddings)
    print('done')


    print('calculating similarities...', end='')
    start = time.time()
    D, I = index.search(
        embeddings,
        INITIAL_CALCULATION
    )
    end = time.time()
    print(f'took {int((end-start)*1000)}ms')


    counter = 0

    print('done')

    similarities = []

    cnt = 0
    for i in range(0, len(D)):

        print(f'filtering and storing data... { round(cnt/len(D)*100) }%', end='\r')
        cnt += 1

        uid = results[i][0]

        similarities += [
            [
                uid,
                results[I[i][i2]][0],
                scale(D[i][i2]) if i >= I[i][i2] else 0  # remove duplicates; very important to keep exact matches i=I for the matching algorithm
            ]
            for i2 in range(0, len(D[i]))
        ]

        if len(similarities) > CHUNK_SIZE or i == len(D)-1:

            # remove non-relevant similarities
            similarities = list(filter(lambda elm: elm[2] > 0, similarities))

            # commit to db
            ingest(similarities)

            similarities = []