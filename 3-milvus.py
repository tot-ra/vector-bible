import struct
import time

from sentence_transformers import SentenceTransformer
import hashlib
md5_hash = hashlib.md5()

from common import read_verses

from pymilvus import MilvusClient, DataType, Collection

collection_name = "collection_768"

# 1. Set up a Milvus client
client = MilvusClient(
    uri="http://localhost:19530"
)

# 2. Create a collection in quick setup mode

if not client.has_collection(collection_name):
    client.create_collection(
        collection_name=collection_name,
        dimension=768,
        id_type=DataType.VARCHAR,
        max_length=32,
        # auto_id=True
    )
    client.create_index(
        collection_name=collection_name,
        index_params={
          "metric_type":"L2",
          "index_type":"HNSW",
          "params":{"nlist":1024}
        }
    )
#
# res = client.get_load_state(
#     collection_name=collection_name
# )

def milvus_inserts(chunk):
    start_time = time.perf_counter()
    data = []
    for id, text, meta, embedding in chunk:
        md5_hash.update(id.encode('utf-8'))
        id = md5_hash.hexdigest()

        # Ensure embedding is a list of floats
        if isinstance(embedding, bytes):
            embedding = list(struct.unpack(f'{len(embedding) // 4}f', embedding))

        data.append(
            {"id": id, "vector": embedding, "text": text, "meta": meta}
        )

    client.insert(collection_name=collection_name, data=data)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"batch insert: {elapsed_time} sec")


start_time = time.perf_counter()
read_verses(milvus_inserts, minibatch_size=100)
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Insertion time: {elapsed_time} sec")