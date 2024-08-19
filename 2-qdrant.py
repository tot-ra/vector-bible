import struct
import time

from qdrant_client import QdrantClient
from qdrant_client.grpc import Filter, FieldCondition
from qdrant_client.http.models import MatchValue
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import hashlib

from common import read_verses

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

client = QdrantClient("0.0.0.0", grpc_port=6334, prefer_grpc=True)
collection_name = "collection_768"
md5_hash = hashlib.md5()

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

def qdrant_inserts(chunk):
    points = []
    for id, text, meta, embedding in chunk:
        md5_hash.update(id.encode('utf-8'))
        id = md5_hash.hexdigest()

        # Ensure embedding is a list of floats
        if isinstance(embedding, bytes):
            embedding = list(struct.unpack(f'{len(embedding) // 4}f', embedding))

        points.append(PointStruct(id=id, vector=embedding, payload={"text":text, "meta":meta}))

    start_time = time.perf_counter()
    client.upsert(
        collection_name,
        wait=False,
        points=points,
    )
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"batch insert: {elapsed_time} sec")


def qdrant_search(text):
    embeddings = model.encode(text)
    search_result = client.search(
        collection_name=collection_name,
        query_vector=embeddings,
        # query_filter=Filter(
        #     must=[FieldCondition(key="city", match=MatchValue(value="London"))]
        # ),
        with_payload=True,
        limit=10,
    )

    print(search_result)

def qdrant_search(text):
    embeddings = model.encode(text)
    search_result = client.search(
        collection_name=collection_name,
        query_vector=embeddings,
        query_filter=Filter(
            must=[FieldCondition(key="city", match=MatchValue(value="London"))]
        ),
        with_payload=True,
        limit=10,
    )

    print(search_result)

start_time = time.perf_counter()

read_verses(qdrant_inserts, minibatch_size=100)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Insertion time: {elapsed_time} sec")


start_time = time.perf_counter()

qdrant_search("воскресил из мертвых")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Search time: {elapsed_time} sec")