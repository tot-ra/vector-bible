import struct
import time

import weaviate
from weaviate.classes.init import AdditionalConfig, Timeout
import hashlib
from weaviate.classes.config import Configure, Property, DataType, VectorDistances
from weaviate.classes.query import MetadataQuery
from sentence_transformers import SentenceTransformer
from common import read_verses

md5_hash = hashlib.md5()

client = weaviate.connect_to_local(
    port=8080,
    grpc_port=50051,
    additional_config=AdditionalConfig(
        timeout=Timeout(init=30, query=60, insert=120)  # Values in seconds
    )
)  # Connect with default parameters

collection_name = "collection_768"
try:
    collection = client.collections.get(collection_name)
except weaviate.exceptions.UnexpectedStatusCodeError as e:
    collection = client.collections.create(
        name=collection_name,
        vector_index_config=Configure.VectorIndex.hnsw(
            distance_metric=VectorDistances.COSINE
        ),
        properties=[
            Property(
                name="text",
                data_type=DataType.TEXT,
             ),
            Property(
                name="meta",
                data_type=DataType.OBJECT,
                index_filterable=True,
                index_searchable=True,
             ),
        ]
    )

def weaviate_inserts(chunk):
    # collection = client.collections.get(collection_name)

    data = []
    for id, text, meta, embedding in chunk:
        # md5_hash.update(id.encode('utf-8'))
        # id = md5_hash.hexdigest()

        # Ensure embedding is a list of floats
        if isinstance(embedding, bytes):
            embedding = list(struct.unpack(f'{len(embedding) // 4}f', embedding))

        data.append(
            {"embedding": embedding, "text": text, "meta": meta}
        )

    start_time = time.perf_counter()
    with collection.batch.dynamic() as batch:
        for data_row in data:
            batch.add_object(
                properties={"text": data_row["text"], "meta": data_row["meta"]},
                vector=data_row["embedding"],
            )

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"batch insert: {elapsed_time} sec")

    print(collection.batch.failed_objects)
    return elapsed_time

def weaviate_search(text):
    response = collection.query.near_vector(
        near_vector=embeddings,
        limit=10,
        return_metadata=MetadataQuery(distance=True)
    )

    for o in response.objects:
        print(f"Text: {o.properties['text']}; Similarity: {1-o.metadata.distance}")

read_verses(weaviate_inserts, max_items=24000, minibatch_size=1000)

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
embeddings = model.encode("воскресил из мертвых")

start_time = time.perf_counter()
weaviate_search(embeddings)
weaviate_search(embeddings)
weaviate_search(embeddings)
weaviate_search(embeddings)
weaviate_search(embeddings)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Search time: {elapsed_time/5} sec")