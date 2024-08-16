# Vector DBs comparison sandbox on a Biblical study
Goal of this repo is to compare different vector databases in terms of performance, load,
ease of use and features.

<img width="300" alt="Screenshot 2024-08-17 at 02 35 25" src="https://github.com/user-attachments/assets/cbb7b69c-ad9c-4cf7-8955-f8e562b93ad7">


## Candidates

| Engine                                                                 |Ports| UI
|------------------------------------------------------------------------|--|--|
| Postgres 14.9 + [pgvector 0.7.4](https://github.com/pgvector/pgvector) |5432|
| [Qdrant 1.11.0](https://github.com/qdrant/qdrant)                       |6333| http://localhost:6333/dashboard#/collections |
| [Milvus 2.4.8](https://github.com/milvus-io/milvus)                    |9091 19530|
| [Weviate 1.24.22](https://github.com/weaviate/weaviate)                |8080 50051 |
| [ChromaDB 0.5.4](https://github.com/chroma-core/chroma)                | 8000 |
| Redis                                                                  | 6379 |
| Elastic                                                                |  |


```bash
docker-compose -f docker-compose.qdrant.yml up qdrant
docker-compose -f docker-compose.pgvector.yml up postgres --build
docker-compose -f docker-compose.weaviate.yml up weaviate
docker-compose -f docker-compose.milvus.yml up
docker-compose -f docker-compose.chromadb.yml up
```


## Testing text data
Basic test is to load bible text data in different languages and compare search performance

### Steps
- Download SQLite data for bible in different languages
https://bible.helloao.org/bible.db (8.4GB)
- Spin up vector databases one by one
- Create database/collection

#### Test cases
- Generate embeddings for each verse using multilingual embed model with 512 dim
  - Insert embeddings one-by-one [measure latency]
  - Insert embeddings in batch [measure latency]
  - Run search [measure latency, accuracy]

### Environment
- python 3.11
- local mac
- single-container dockerized vector databases
```
python -m pip install 'qdrant-client[fastembed]'

# https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2
pip install -U sentence-transformers
```
