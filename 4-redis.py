"""
Code samples for vector database quickstart pages:
    https://redis.io/docs/latest/develop/get-started/vector-database/
"""

import json
import numpy as np
import redis
import time

from redis.commands.search.field import VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer

from common import read_verses


key_prefix = "verse"
client = redis.Redis(host="localhost", port=6379, password="pass")


def create_redis_index(index_name):
    try:
        # check to see if index exists
        client.ft(index_name).info()
        print("Index already exists!")
    except:
        VECTOR_DIMENSION = 768
        schema = (
            # TextField("$.meta", no_stem=True, as_name="meta"),
            # TextField("$.text", as_name="text"),
            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": VECTOR_DIMENSION,
                    "DISTANCE_METRIC": "COSINE",
                },
            ),
        )
        definition = IndexDefinition(
            prefix=[f"{key_prefix}:"], index_type=IndexType.HASH
        )
        client.ft(index_name).create_index(fields=schema, definition=definition)


def redis_inserts(chunk, pipeline):
    # pipeline = client.pipeline()
    for _id, text, meta, embedding in chunk:
        key = f"{key_prefix}:{_id}"

        # Convert embedding from ndarray to byte string
        if isinstance(embedding, (np.ndarray, list)):
            embedding = np.array(embedding, dtype=np.float32).tobytes()

        if not isinstance(meta, str):
            meta = json.dumps(meta)

        pipeline.hset(
            name=key,
            mapping={
                "text": text,
                "meta": meta,
                "embedding": embedding,
            },
        )

    start_time = time.perf_counter()
    pipeline.execute()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Insert time: {elapsed_time} sec")

    return elapsed_time


def redis_search(embeddings, index_name):
    query = (
        Query("(*)=>[KNN 10 @embedding $query_vector AS vector_score]")
        .sort_by("vector_score")
        .paging(0, 10)
        .return_fields("vector_score", "id", "text")
        .dialect(4)
    )

    # query = (
    #     Query(
    #         "@embedding:[VECTOR_RANGE $range $query_vector]=>"
    #         "{$YIELD_DISTANCE_AS: vector_score}"
    #     )
    #     .sort_by("vector_score")
    #     .return_fields("vector_score", "id", "text")
    #     .paging(0, 10)
    #     .dialect(2)
    # )

    result_docs = (
        client.ft(index_name)
        .search(
            query,
            {"query_vector": np.array(embeddings, dtype=np.float32).tobytes()},
            #            | ({"range": 0.55}),
        )
        .docs
    )

    for doc in result_docs:
        vector_score = round(1 - float(doc.vector_score), 2)

        print(f"Text: {doc.text}; Similarity: {vector_score}")


# Create Index
index_name = "idx:verse_vss12"
create_redis_index(index_name)

# Ingest Data
# with client.pipeline(transaction=False) as pipeline:
#     read_verses(redis_inserts, max_items=24000, minibatch_size=1000, pipeline=pipeline)

# Run queries
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)
embeddings = model.encode("воскресил из мертвых")

start_time = time.perf_counter()

redis_search(embeddings, index_name)
redis_search(embeddings, index_name)
redis_search(embeddings, index_name)
redis_search(embeddings, index_name)
redis_search(embeddings, index_name)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Search time: {elapsed_time/5} sec")
