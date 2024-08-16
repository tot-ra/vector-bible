from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import hashlib

from index import scripture

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')


client = QdrantClient("0.0.0.0", grpc_port=6334, prefer_grpc=True)
collection_name = "collection_768"
md5_hash = hashlib.md5()

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.DOT),
    )

def qdrant_handler(id, text):
    embeddings = model.encode(text)
    md5_hash.update(id.encode('utf-8'))
    id = md5_hash.hexdigest()

    print(id)
    print(text)
    print(embeddings)

    client.upsert(
        collection_name,
        wait=True,
        points=[
            PointStruct(id=id, vector=embeddings, payload={"text":text}),
        ],
    )

scripture(qdrant_handler)