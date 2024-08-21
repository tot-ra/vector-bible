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
from common import read_verses
import time
md5_hash = hashlib.md5()

client = redis.Redis(host="localhost", port=6379, password="pass", decode_responses=True)
VECTOR_DIMENSION = 768

schema = (
    TextField("$.meta", no_stem=True, as_name="meta"),
    TextField("$.text", as_name="description"),
    VectorField(
        "$.embedding",
        "FLAT",
        {
            "TYPE": "FLOAT32",
            "DIM": VECTOR_DIMENSION,
            "DISTANCE_METRIC": "COSINE",
        },
        as_name="embedding",
    ),
)
definition = IndexDefinition(prefix=["verse:"], index_type=IndexType.JSON)
res = client.ft("idx:verse_vss").create_index(fields=schema, definition=definition)

def redis_inserts(chunk):
    pipeline = client.pipeline()
    for id, text, meta, embedding in chunk:
        md5_hash.update(id.encode('utf-8'))
        id = md5_hash.hexdigest()

        # Convert embedding from ndarray to list
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()


        pipeline.json().set(f"verse:{id}", "$", {
            "text": text,
            "meta": meta,
            "embedding": embedding,
        })
    pipeline.execute()


start_time = time.perf_counter()

read_verses(redis_inserts, minibatch_size=1000)

# redis_search("воскресил из мертвых")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Insert time: {elapsed_time} sec")


# info = client.ft("idx:bikes_vss").info()
# num_docs = info["num_docs"]
# indexing_failures = info["hash_indexing_failures"]
# print(f"{num_docs} documents indexed with {indexing_failures} failures")
# >>> 11 documents indexed with 0 failures

# query = Query("@brand:Peaknetic")
# res = client.ft("idx:bikes_vss").search(query).docs
# # print(res)
# # >>> [
# #       Document {
# #           'id': 'bikes:008',
# #           'payload': None,
# #           'brand': 'Peaknetic',
# #           'model': 'Soothe Electric bike',
# #           'price': '1950', 'description_embeddings': ...

# query = Query("@brand:Peaknetic").return_fields("id", "brand", "model", "price")
# res = client.ft("idx:bikes_vss").search(query).docs
# # print(res)
# # >>> [
# #       Document {
# #           'id': 'bikes:008',
# #           'payload': None,
# #           'brand': 'Peaknetic',
# #           'model': 'Soothe Electric bike',
# #           'price': '1950'
# #       },
# #       Document {
# #           'id': 'bikes:009',
# #           'payload': None,
# #           'brand': 'Peaknetic',
# #           'model': 'Secto',
# #           'price': '430'
# #       }
# # ]

# query = Query("@brand:Peaknetic @price:[0 1000]").return_fields(
#     "id", "brand", "model", "price"
# )
# res = client.ft("idx:bikes_vss").search(query).docs
# # print(res)
# # >>> [
# #       Document {
# #           'id': 'bikes:009',
# #           'payload': None,
# #           'brand': 'Peaknetic',
# #           'model': 'Secto',
# #           'price': '430'
# #       }
# # ]

# queries = [
#     "Bike for small kids",
#     "Best Mountain bikes for kids",
#     "Cheap Mountain bike for kids",
#     "Female specific mountain bike",
#     "Road bike for beginners",
#     "Commuter bike for people over 60",
#     "Comfortable commuter bike",
#     "Good bike for college students",
#     "Mountain bike for beginners",
#     "Vintage bike",
#     "Comfortable city bike",
# ]
#
# encoded_queries = embedder.encode(queries)
# len(encoded_queries)
# # >>> 11


# def create_query_table(query, queries, encoded_queries, extra_params=None):
#     """
#     Creates a query table.
#     """
#     results_list = []
#     for i, encoded_query in enumerate(encoded_queries):
#         result_docs = (
#             client.ft("idx:bikes_vss")
#             .search(
#                 query,
#                 {"query_vector": np.array(encoded_query, dtype=np.float32).tobytes()}
#                 | (extra_params if extra_params else {}),
#             )
#             .docs
#         )
#         for doc in result_docs:
#             vector_score = round(1 - float(doc.vector_score), 2)
#             results_list.append(
#                 {
#                     "query": queries[i],
#                     "score": vector_score,
#                     "id": doc.id,
#                     "brand": doc.brand,
#                     "model": doc.model,
#                     "description": doc.description,
#                 }
#             )
#
#     # Optional: convert the table to Markdown using Pandas
#     queries_table = pd.DataFrame(results_list)
#     queries_table.sort_values(
#         by=["query", "score"], ascending=[True, False], inplace=True
#     )
#     queries_table["query"] = queries_table.groupby("query")["query"].transform(
#         lambda x: [x.iloc[0]] + [""] * (len(x) - 1)
#     )
#     queries_table["description"] = queries_table["description"].apply(
#         lambda x: (x[:497] + "...") if len(x) > 500 else x
#     )
#     return queries_table.to_markdown(index=False)
#
#
#
# query = (
#     Query("(*)=>[KNN 3 @vector $query_vector AS vector_score]")
#     .sort_by("vector_score")
#     .return_fields("vector_score", "id", "brand", "model", "description")
#     .dialect(2)
# )
#
# table = create_query_table(query, queries, encoded_queries)
# print(table)
# # >>> | Best Mountain bikes for kids     |    0.54 | bikes:003...
#
# hybrid_query = (
#     Query("(@brand:Peaknetic)=>[KNN 3 @vector $query_vector AS vector_score]")
#     .sort_by("vector_score")
#     .return_fields("vector_score", "id", "brand", "model", "description")
#     .dialect(2)
# )
# table = create_query_table(hybrid_query, queries, encoded_queries)
# print(table)
# # >>> | Best Mountain bikes for kids     |    0.3  | bikes:008...
#
# range_query = (
#     Query(
#         "@vector:[VECTOR_RANGE $range $query_vector]=>"
#         "{$YIELD_DISTANCE_AS: vector_score}"
#     )
#     .sort_by("vector_score")
#     .return_fields("vector_score", "id", "brand", "model", "description")
#     .paging(0, 4)
#     .dialect(2)
# )
# table = create_query_table(
#     range_query, queries[:1],
#     encoded_queries[:1],
#     {"range": 0.55}
# )
# print(table)
# >>> | Bike for small kids |    0.52 | bikes:001 | Velorim    |...
