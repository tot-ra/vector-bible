import struct
import time

import marqo
import numpy as np
from sentence_transformers import SentenceTransformer

from common import read_verses

mq = marqo.Client(url='http://localhost:8882')

collection_name = "collection_768v25"
mq.create_index(collection_name)

# , settings_dict={
#     "type": "unstructured",
#     # "allFields": [
#     #     {"name": "meta", "type": "text"},
#     #     {"name": "custom", "type": "custom_vector"},
#     # ],
#     # "tensorFields": ["custom"],
# }

index = mq.index(collection_name)

def marqo_inserts(chunk):
    docs = []
    for id, text, meta, embedding in chunk:
        if isinstance(embedding, bytes):
            embedding = list(struct.unpack(f'{len(embedding) // 4}f', embedding))

        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        docs.append({
            "custom": {
                "content": text,
                "vector": embedding
            },
            # "meta": meta,
            "_id": id
        })

    start_time = time.perf_counter()
    res = index.add_documents(docs, tensor_fields=["custom"], mappings={
        "custom": {"type": "custom_vector"},
    })
    print(res)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"batch insert: {elapsed_time} sec")

    return elapsed_time

def marqo_search(embedding):
    if isinstance(embedding, bytes):
        embedding = list(struct.unpack(f'{len(embedding) // 4}f', embedding))

    if isinstance(embedding, np.ndarray):
        embedding = embedding.tolist()

    mq.index(collection_name).search(
        q={
            "custom" : {"vector": embedding}
        },
    )

read_verses(marqo_inserts, max_items=24000, minibatch_size=128)


model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
embeddings = model.encode("воскресил из мертвых")

start_time = time.perf_counter()
marqo_search(embeddings)
# marqo_search(embeddings)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Search time: {elapsed_time} sec")