## Vector DBs comparison sandbox on a Biblical multilingual 10M verses

Goal of this repo is to compare different vector databases in terms of performance, load,
ease of use and features.

<img width="800" alt="Screenshot 2024-08-17 at 02 46 07" src="https://github.com/user-attachments/assets/29068c19-1a2c-41ab-a15f-a0eeb92d3a2a">


## Candidates

| Engine                                                                 | Ports      | URLs                                                 
|------------------------------------------------------------------------|------------|----------------------------------------------------|
| Postgres 16.4 + [pgvector 0.7.4](https://github.com/pgvector/pgvector) | 5432       |
| [Qdrant 1.11.0](https://github.com/qdrant/qdrant)                      | 6333       | [UI](http://localhost:6333/dashboard#/collections) |
| [Milvus 2.4.8](https://github.com/milvus-io/milvus)                    | 9091 19530 |
| [Weviate 1.24.22](https://github.com/weaviate/weaviate)                | 8080 50051 |
| [ChromaDB 0.5.4](https://github.com/chroma-core/chroma)                | 8000       |
| Redis                                                                  | 6379       |
| Elastic                                                                |            |

### Testing Environment

- python 3.11
- local mac M3 32GB
- single-container dockerized vector databases


## Testing text data

Basic test is to load bible text data in different languages and compare search performance

### Steps
- Download SQLite data for bible in different languages
  https://bible.helloao.org/bible.db (8.4GB)
- Pre-Generate embeddings and store them in `ChapterVerse`. 
Use multilingual embed model with **768 dim**.
https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2
- Spin up vector database you want to test

```
# https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2
pip install -U sentence-transformers


# Generate embeddings into SQLite
# This will take a while
# You can re-run it to continue from where it stopped
python 0-generate-embeddings.py
```

### 1. Postgres + pgvector
Was unable to install pgvector on Postgres 14 and 15, so used Postgres 16.4

```
docker-compose -f docker-compose.pgvector.yml up postgres --build
```

### 2. Qdrant
```
docker-compose -f docker-compose.qdrant.yml up qdrant

python -m pip install 'qdrant-client'

# Test Qdrant
python 2-qdrant.py
```


### Others
```bash
docker-compose -f docker-compose.milvus.yml up
docker-compose -f docker-compose.weaviate.yml up weaviate
docker-compose -f docker-compose.chromadb.yml up
```

## Results
Most of time is spent on embedding generation

| Engine | Details  | Insert 10M, batch 100 | Search top 10 | Search with filter|
|--------|----------|-----------------------|---------------|--|
| Qdrant | Cosine,  | 786 sec (no wait)     | 0.214 sec     |--|
