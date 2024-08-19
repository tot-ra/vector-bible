import time

from qdrant_client import QdrantClient
from qdrant_client.grpc import Filter, FieldCondition
from qdrant_client.http.models import MatchValue
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import hashlib

from index import read_verses

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

client = QdrantClient("0.0.0.0", grpc_port=6334, prefer_grpc=True)
collection_name = "collection_768"
md5_hash = hashlib.md5()

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.DOT),
    )

def qdrant_handler(chunk):
    for id, text, meta in chunk:
        embeddings = model.encode(text)
        md5_hash.update(id.encode('utf-8'))
        id = md5_hash.hexdigest()

        start_time = time.perf_counter()
        client.upsert(
            collection_name,
            wait=False,
            points=[
                PointStruct(id=id, vector=embeddings, payload={"text":text, "meta":meta}),
            ],
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

start_time = time.perf_counter()

# read_verses(qdrant_handler, minibatch_size=100)
qdrant_search("воскресил из мертвых")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} sec")