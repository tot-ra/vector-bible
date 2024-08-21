"""
Code samples for vector database quickstart pages:
    https://redis.io/docs/latest/develop/get-started/vector-database/
"""
import struct

import numpy as np
import pandas as pd
import redis
from redis.commands.search.field import (
    NumericField,
    TagField,
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import hashlib

from sentence_transformers import SentenceTransformer

from common import read_verses
import time
md5_hash = hashlib.md5()

client = redis.Redis(host="localhost", port=6379, password="pass", decode_responses=True)

def redis_index(index_name):
    VECTOR_DIMENSION = 768
    schema = (
        # TextField("$.meta", no_stem=True, as_name="meta"),
        TextField("$.text", as_name="text"),
        VectorField(
            "$.embedding",
            "HNSW",
            {
                "TYPE": "FLOAT32",
                "DIM": VECTOR_DIMENSION,
                "DISTANCE_METRIC": "COSINE",
            },
            as_name="embedding",
        ),
    )
    definition = IndexDefinition(prefix=["verse:"], index_type=IndexType.JSON)
    res = client.ft(index_name).create_index(fields=schema, definition=definition)
    print(res)

def redis_inserts(chunk):
    start_time = time.perf_counter()
    pipeline = client.pipeline()
    for id, text, meta, embedding in chunk:
        md5_hash.update(id.encode('utf-8'))
        id = md5_hash.hexdigest()

        # Convert embedding from ndarray to list
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()


        pipeline.json().set(f"verse:{id}", "$", {
            "text": text,
            # "meta": meta,
            "embedding": embedding,
        })
    pipeline.execute()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Insert time: {elapsed_time} sec")

def redis_search(text, index_name):
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

    embeddings = model.encode(text)

    # query = (
    #     Query("(*)=>[KNN 10 @embedding $query_vector AS vector_score]")
    #     .sort_by("vector_score")
    #     .return_fields("vector_score", "id", "text")
    #     .dialect(2)
    # )

    range_query = (
        Query(
            "@embedding:[VECTOR_RANGE $range $query_vector]=>"
            "{$YIELD_DISTANCE_AS: vector_score}"
        )
        .sort_by("vector_score")
        .return_fields("vector_score", "id", "text")
        .paging(0, 10)
        .dialect(2)
    )

    result_docs = (
        client.ft(index_name)
        .search(
            range_query,
            {"query_vector": np.array(embeddings, dtype=np.float32).tobytes()}
            | ({"range": 0.55}),
        )
        .docs
    )

    for doc in result_docs:
        vector_score = round(1 - float(doc.vector_score), 2)

        print(f"Text: {doc.text}; Similarity: {vector_score}")


index_name = "idx:verse_vss10"
redis_index(index_name)
read_verses(redis_inserts, minibatch_size=1000)

start_time = time.perf_counter()
redis_search("воскресил из мертвых", index_name)
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Search time: {elapsed_time} sec")