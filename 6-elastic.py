from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

es_client = Elasticsearch(
    "https://localhost:9200",
    # ssl_assert_fingerprint='AA:BB:CC:3C:A4:99:12:A8:D6:41:B7:A6:52:ED:CA:2E:0E:64:E2:0E:A7:8F:AE:4C:57:0E:4B:A3:00:11:22:33',
    basic_auth=("elastic", "passw0rd")
)


# Search
def elastic_search(embedding):
    query_string = {
        "field": "title_embedding",
        "query_vector": embedding,
        "k": 1,
        "num_candidates": 10
    }
    results = es_client.search(index="movies", knn=query_string, source_includes=["text"])

    print(results['hits']['hits'])


model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
embeddings = model.encode("воскресил из мертвых")
elastic_search(embeddings)