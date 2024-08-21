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

    # index_params = client.prepare_index_params()
    # index_params.add_index(
    #     field_name="vector",
    #     index_type="HNSW",
    #     metric_type="L2",
    #     params={"nlist": 1024}
    # )

    # collection.create_index(
    #     field_name="vector",
    #     index_params={
    #         "index_type": "HNSW",
    #         "metric_type": "L2",
    #         "params": {
    #             "M": 256,
    #             "efConstruction": 256
    #         }
    #     },
    #     index_name=""
    # )


#
# res = client.get_load_state(
#     collection_name=collection_name
# )

def milvus_inserts(chunk):
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


def milvus_search(text):
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

    embeddings = model.encode(text)
    search_result = client.search(
        collection_name=collection_name,
        data=[embeddings],
        limit=10,
        params={"metric_type": "L2", "params": {"nprobe": 10}},
        anns_field="vector",
        consistency_level="Strong",
        output_fields=["text"]
    )

    # print(search_result)
    # cycle through search results
    for result in search_result[0]:
        print(f"Text: {result['entity']['text']}; Similarity: {result['distance']}")


start_time = time.perf_counter()
# read_verses(milvus_inserts, minibatch_size=1000)

milvus_search("воскресил из мертвых")
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Search time: {elapsed_time} sec")
