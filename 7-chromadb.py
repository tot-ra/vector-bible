import chromadb
import struct
import time
import hashlib
import numpy as np
from common import read_verses
from sentence_transformers import SentenceTransformer

md5_hash = hashlib.md5()

# setup Chroma in-memory, for easy prototyping. Can add persistence easily!
client = chromadb.Client(
    settings=chromadb.Settings(
    chroma_server_host='localhost', chroma_server_http_port=18000
    ))

collection_name = "collection_768ru2"
# Create collection. get_collection, get_or_create_collection, delete_collection also available!
# collection = client.get_collection(name=collection_name)
collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})

def chroma_inserts(chunk):
    start_time = time.perf_counter()

    for id, text, meta, embedding in chunk:
        md5_hash.update(id.encode('utf-8'))
        id = md5_hash.hexdigest()

        # Ensure embedding is a list of floats
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()


        collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[meta],
            ids=[id],
        )

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"batch insert: {elapsed_time} sec")

    return elapsed_time

def chroma_filter_search(embeddings):
    # # Query/search 2 most similar results. You can also .get by id
    results = collection.query(
        query_embeddings=[embeddings],
        n_results=10,
        # where={"metadata_field": "is_equal_to_this"}, # optional filter
        # where_document={"$contains":"search_string"}  # optional filter
    )

    # print(results)
    documents = results['documents'][0]  # The documents list is nested inside another list
    distances = results['distances'][0]  # The documents list is nested inside another list

    for text, distance in zip(documents, distances):
        print(f"Text: {text}; Similarity: {1-distance}")



read_verses(chroma_inserts, max_items=24000, minibatch_size=1000)

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
embeddings = model.encode("воскресил из мертвых")
embeddings = embeddings.tolist()

start_time = time.perf_counter()

chroma_filter_search(embeddings)
chroma_filter_search(embeddings)
chroma_filter_search(embeddings)
chroma_filter_search(embeddings)
chroma_filter_search(embeddings)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Search time: {elapsed_time/5} sec")