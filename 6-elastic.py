import time

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from common import read_verses

es_client = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "adminadmin")
)

def elastic_inserts(chunk):
    start_time = time.perf_counter()
    for id, text, meta, embedding in chunk:
        es_client.index(index="verses", document={
            "text": text,
            "meta": meta,
            "embedding": embedding
        })
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"batch insert: {elapsed_time} sec")

    return elapsed_time

def elastic_search(embedding):
    results = es_client.search(index="verses", knn={
        "field": "embedding",
        "query_vector": embedding,
        "k": 10,
        "num_candidates": 10
    }, source_includes=["text"])

    for row in results['hits']['hits']:
        print(f"Text: {row['_source']['text']}; Similarity: {row['_score']}")


read_verses(elastic_inserts, max_items=1400000, minibatch_size=1000)

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
embeddings = model.encode("воскресил из мертвых")

start_time = time.perf_counter()

elastic_search(embeddings)
elastic_search(embeddings)
elastic_search(embeddings)
elastic_search(embeddings)
elastic_search(embeddings)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Search time: {elapsed_time/5} sec")