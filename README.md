# Vector DBs comparison sandbox on a Biblical study

Goal of this repo is to compare different vector databases in terms of performance, load,
ease of use and features.

## Candidates

| Engine                                                                 | Ports      | UI                                           
|------------------------------------------------------------------------|------------|----------------------------------------------|
| Postgres 14.9 + [pgvector 0.7.4](https://github.com/pgvector/pgvector) | 5432       |
| [Qdrant 1.11.0](https://github.com/qdrant/qdrant)                      | 6333       | http://localhost:6333/dashboard#/collections |
| [Milvus 2.4.8](https://github.com/milvus-io/milvus)                    | 9091 19530 |
| [Weviate 1.24.22](https://github.com/weaviate/weaviate)                | 8080 50051 |
| [ChromaDB 0.5.4](https://github.com/chroma-core/chroma)                | 8000       |
| Redis                                                                  | 6379       |
| Elastic                                                                |            |

```bash
docker-compose -f docker-compose.qdrant.yml up qdrant
docker-compose -f docker-compose.pgvector.yml up postgres --build
docker-compose -f docker-compose.weaviate.yml up weaviate
docker-compose -f docker-compose.milvus.yml up
docker-compose -f docker-compose.chromadb.yml up
```

## Testing text data on 22955 verses from the Bible

Basic test is to load bible text data in different languages and compare search performance

### Steps

- Download SQLite data for bible in different languages
  https://bible.helloao.org/bible.db (8.4GB)
- Spin up vector databases one by one
- Create database/collection

#### Test cases

- Generate embeddings for each verse using multilingual embed model with 768 dim
- Insert embeddings in batch of 100 [measure time]
- Run search [measure time, accuracy]


#### Results
Most of time is spent on embedding generation
Statistics - 22955 verses in total

| Engine |  Insert 23k, batch 100 | Search top 10 |
|--------|-----------------------|---------------|
| Qdrant |  786 sec (no wait)     | 0.169 sec     |

### Environment

- python 3.11
- local mac
- single-container dockerized vector databases

```
python -m pip install 'qdrant-client[fastembed]'

# https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2
pip install -U sentence-transformers
```