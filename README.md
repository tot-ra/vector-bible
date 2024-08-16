# Vector dbs benchmarking

## Setup

| Engine                                                                 |Ports|
|------------------------------------------------------------------------|--|
| Postgres 14.9 + [pgvector 0.7.4](https://github.com/pgvector/pgvector) |5432|
| [Qdrant 0.3.0](https://github.com/qdrant/qdrant)                       |6333|
| [Milvus 2.4.8](https://github.com/milvus-io/milvus)                    |9091 19530|
| [Weviate 1.24.22](https://github.com/weaviate/weaviate)                |8080 50051 |
| [ChromaDB 0.5.4](https://github.com/chroma-core/chroma)                | 8000 |
```bash
docker-compose -f docker-compose.qdrant.yml up qdrant
docker-compose -f docker-compose.pgvector.yml up postgres --build
docker-compose -f docker-compose.weaviate.yml up weaviate
docker-compose -f docker-compose.milvus.yml up
docker-compose -f docker-compose.chromadb.yml up
```


## Testing embeddings from text data
Download SQLite data for bible in different languages
https://bible.helloao.org/bible.db (8.4GB)
