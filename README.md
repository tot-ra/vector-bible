# Vector dbs benchmarking
## Text data
Download SQLite data for bible in different languages
https://bible.helloao.org/bible.db (8.4GB)

```bash
docker-compose -f docker-compose.qdrant.yml --verbose up qdrant
docker-compose -f docker-compose.pgvector.yml --verbose up postgres --build
```