## Vector DBs comparison sandbox on a Biblical multilingual 10M verses

Goal of this repo is to compare different vector databases in terms of performance, load,
ease of use and features.

https://github.com/user-attachments/assets/a622727e-deb7-4b55-95e2-0642bd6f4763

## Candidates & Results

Most of time is spent on embedding generation (days)
Note that insertion also includes md5 hash generation.

| Nr | Engine                                                                 | Ports                                                     | Insert speed (1k batch) | Similarity search <br />on 24k dataset | Similarity search      | Ease of integration 🤯 |
|----|------------------------------------------------------------------------|-----------------------------------------------------------|-------------------------|----------------------------------------|------------------------|------------------------|
| 1  | Postgres 16.4 + [pgvector 0.7.4](https://github.com/pgvector/pgvector) | 5432                                                      | N/A                     | 0.216 sec                              | --                     | ★★☆☆☆                  |               
| 2  | [Qdrant 1.11.0](https://github.com/qdrant/qdrant)                     | 6334 [6333](http://localhost:6333/dashboard#/collections) | 1.92 sec                | 0.140 sec                              | 2.525 sec on 760k rows | ★★★★☆                  |
| 3  | [Milvus 2.4.8](https://github.com/milvus-io/milvus)                   | 9091 19530 [8000](http://localhost:8000)                  | 1.91 sec                | 2.718 sec                              | 4.216 sec on 814k rows | ★★★☆☆                  |
| 4  | [Redis stack 7.4](https://github.com/redis/redis)                     | 6379 [8001](http://localhost:8001/)                       | 0.380 sec +- 0.02 sec   | 3.219 sec                              | --                     | ★★☆☆☆                  | 
| 5  | [Weviate 1.24.22](https://github.com/weaviate/weaviate)                | 8080 50051                                                |                         |                                        | --                     |                        |
| 6  | [ChromaDB 0.5.4](https://github.com/chroma-core/chroma)                | 8000                                                      |                         |                                        | --                     |                        |
| 7  | Elastic                                                                |                                                           |                         |                                        | --                     |                        |

### Testing Environment

- python 3.11
- local mac M3 32GB
- single-container dockerized vector databases

## Testing text data

Basic test is to load bible text data in different languages and compare search performance

### Data preparation

- Download SQLite data for bible in different languages
  https://bible.helloao.org/bible.db (8.4GB)
- Export `ChapterVerse` from SQLIte to Postgres for better performance. You will need some tool like IntelliJ DataGrip.
  You could use sqlite but it would be very slow.
- Add column `ChapterVerse.embedding` with `store.vector(768)` type
- Create index in postgres for faster updates

```mermaid
flowchart LR
sqlite -- " 0 - import manually in IDE " --> postgres 
postgres -- " text " --> 1-pgvector.py -- " 1 - generate embeddings " --> postgres[( postgres )]
```
```
  create index ChapterVerse_translationid_bookid_chapternumber_number_index
    on store."ChapterVerse" (translationid, bookid, chapternumber, number);
  ```

- Pre-Generate embeddings and store them in same `ChapterVerse`.
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
✅ Fast search
✅ Data is stored in Postgres, so no need to sync data between databases
🟡 Operators are not the most intuitive
❌ could not install pgvector on Postgres 14 and 15, only version 16 worked
❌ faced `psycopg2.errors.UndefinedFunction: operator does not exist: text <-> vector` when installing extension because
  operators were installed into public schema instead of `store`. Had to reset the image and set extension installation under `store` schema.


```
docker-compose -f docker-compose.pgvector.yml up postgres --build
python -m pip install "psycopg[binary]"
python 1-pgvector.py
```

#### How to visualize embeddings

You can use [cosmograph](https://cosmograph.app/run/)  online tool to visualize nodes and edges.

Export nodes into CSV:

```sql
SELECT CONCAT(translationid, '-', bookid, '-', chapternumber, '-', number) as id,
       text                                                                as label
FROM store."ChapterVerse"
WHERE embedding IS NOT NULL
  AND translationId = 'rus_syn'
  AND bookid IN ('JHN', 'LUK', 'MRK', 'MAT') LIMIT 10000;
```

Export edges into CSV:

```sql
SET
search_path TO store;
WITH pairwise_similarity
         AS (SELECT CONCAT(t1.translationid, '-', t1.bookid, '-', t1.chapternumber, '-', t1.number) AS source,
                    CONCAT(t2.translationid, '-', t2.bookid, '-', t2.chapternumber, '-', t2.number) AS target,
                    1 - (t1.embedding <=> t2.embedding)                                             AS similarity
             FROM store."ChapterVerse" t1,
                  store."ChapterVerse" t2
             WHERE t1.bookid IN ('JHN', 'LUK', 'MRK', 'MAT')
               AND t2.bookid IN ('JHN', 'LUK', 'MRK', 'MAT')
               AND t1.translationId = 'rus_syn'
               AND t2.translationId = 'rus_syn'
               AND t1.embedding IS NOT NULL
               AND t2.embedding IS NOT NULL
               AND CONCAT(t1.translationid, '-', t1.bookid, '-', t1.chapternumber, '-',
                          t1.number) != CONCAT(t2.translationid, '-', t2.bookid, '-', t2.chapternumber, '-', t2.number)
    )
SELECT source,
       target,
       similarity AS weight
FROM pairwise_similarity
WHERE similarity > 0.95
ORDER BY weight DESC LIMIT 10000;

```


<details>
<summary>Postgres similarity results on 24k dataset</summary>
```
Text: чтобы достигнуть воскресения мертвых.; Similarity: 0.9226886199645554
Text: Но Бог воскресил Его из мертвых.; Similarity: 0.8717796943695277
Text: а Начальника жизни убили. Сего Бог воскресил из мертвых, чему мы свидетели.; Similarity: 0.8707684267530202
Text: Но Христос воскрес из мертвых, первенец из умерших.; Similarity: 0.86272182337587
Text: Так и при воскресении мертвых: сеется в тлении, восстает в нетлении;; Similarity: 0.8626047520415614
Text: и что Он погребен был, и что воскрес в третий день, по Писанию,; Similarity: 0.8371098014647679
Text: Ибо как смерть через человека, так через человека и воскресение мертвых.; Similarity: 0.8319413838804383
Text: которою Он воздействовал во Христе, воскресив Его из мертвых и посадив одесную Себя на небесах,; Similarity: 0.8282566644099042
Text: и гробы отверзлись; и многие тела усопших святых воскресли; Similarity: 0.8217248023128517
Text: быв погребены с Ним в крещении, в Нем вы и совоскресли верою в силу Бога, Который воскресил Его из мертвых,; Similarity: 0.8162701932003219
```
</details>

### 2. Qdrant

✅ very clear API and docs
✅ fastest search

```mermaid
flowchart LR
2-qdrant.py -- " read embeddings " --> postgres
2-qdrant.py -- " write over grpc API " --> qdrant[( qdrant )]
```

```
docker-compose -f docker-compose.qdrant.yml up qdrant

python -m pip install 'qdrant-client'

# Test Qdrant
python 2-qdrant.py
```

<img width="600" alt="Screenshot 2024-08-17 at 02 46 07" src="https://github.com/user-attachments/assets/29068c19-1a2c-41ab-a15f-a0eeb92d3a2a">

<details>
<summary>Qdrant similarity results on 24k dataset</summary>

```
Text: чтобы достигнуть воскресения мертвых.; Similarity: 0.9226888418197632
Text: Но Бог воскресил Его из мертвых.; Similarity: 0.8717798590660095
Text: а Начальника жизни убили. Сего Бог воскресил из мертвых, чему мы свидетели.; Similarity: 0.8707683682441711
Text: Но Христос воскрес из мертвых, первенец из умерших.; Similarity: 0.8627219200134277
Text: Так и при воскресении мертвых: сеется в тлении, восстает в нетлении;; Similarity: 0.8626047968864441
Text: и что Он погребен был, и что воскрес в третий день, по Писанию,; Similarity: 0.8371099233627319
Text: Ибо как смерть через человека, так через человека и воскресение мертвых.; Similarity: 0.8319414258003235
Text: которою Он воздействовал во Христе, воскресив Его из мертвых и посадив одесную Себя на небесах,; Similarity: 0.8282566666603088
Text: и гробы отверзлись; и многие тела усопших святых воскресли; Similarity: 0.8217248916625977
Text: быв погребены с Ним в крещении, в Нем вы и совоскресли верою в силу Бога, Который воскресил Его из мертвых,; Similarity: 0.8162703514099121
```
</details>

<details>
<summary>Qdrant similarity results on 760k dataset</summary>

```
Text: чтобы достигнуть воскресения мертвых.; Similarity: 0.9226888418197632
Text: Но Бог воскресил Его из мертвых.; Similarity: 0.8717798590660095
Text: а Начальника жизни убили. Сего Бог воскресил из мертвых, чему мы свидетели.; Similarity: 0.8707683682441711
Text: Но Христос воскрес из мертвых, первенец из умерших.; Similarity: 0.8627219200134277
Text: Так и при воскресении мертвых: сеется в тлении, восстает в нетлении;; Similarity: 0.8626047968864441
Text: и что Он погребен был, и что воскрес в третий день, по Писанию,; Similarity: 0.8371099233627319
Text: Ибо как смерть через человека, так через человека и воскресение мертвых.; Similarity: 0.8319414258003235
Text: যীশু খ্রীষ্টকে স্মরণ করো, যিনি মৃতলোক থেকে পুনরুত্থিত হয়েছেন এবং যিনি দাউদের বংশজাত। এই হল আমার সুসমাচার।; Similarity: 0.827512264251709
Text: in der er gewirkt hat in dem Christus, indem er ihn aus den Toten auferweckte; (und er setzte ihn zu seiner Rechten in den himmlischen Örtern,; Similarity: 0.8242398500442505
Text: и гробы отверзлись; и многие тела усопших святых воскресли; Similarity: 0.8217248916625977
```
</details>

### 3. Milvus
✅ Docs look impressive
🟡 Milvus does not come with built-in UI, so we use `attu` for that.
🟡 Has extra containers
❌ Search was slow, even though it used an index (maybe I did something wrong?)

```mermaid
flowchart LR
3-milvus.py -- " write over grpc API " --> milvus[( milvus )]
3-milvus.py -- " read embeddings " --> postgres
atto["atto\nlocalhost:8000"] --> milvus
```

```bash
python -m pip install pymilvus
docker-compose -f docker-compose.milvus.yml up
```

<img width="600" alt="Screenshot 2024-08-20 at 01 54 28" src="https://github.com/user-attachments/assets/9034e2de-7c11-4cfe-a762-826d01251fff">

<details>
<summary>Milvus similarity results on 24k dataset</summary>

```
Text: чтобы достигнуть воскресения мертвых.; Similarity: 0.7362406253814697
Text: а Начальника жизни убили. Сего Бог воскресил из мертвых, чему мы свидетели.; Similarity: 1.216253399848938
Text: Так и при воскресении мертвых: сеется в тлении, восстает в нетлении;; Similarity: 1.3372809886932373
Text: и что Он погребен был, и что воскрес в третий день, по Писанию,; Similarity: 1.4702727794647217
Text: которою Он воздействовал во Христе, воскресив Его из мертвых и посадив одесную Себя на небесах,; Similarity: 1.538124680519104
Text: Ибо как смерть через человека, так через человека и воскресение мертвых.; Similarity: 1.6495163440704346
Text: Но Бог воскресил Его из мертвых.; Similarity: 1.6659044027328491
Text: Но Христос воскрес из мертвых, первенец из умерших.; Similarity: 1.8069703578948975
Text: быв погребены с Ним в крещении, в Нем вы и совоскресли верою в силу Бога, Который воскресил Его из мертвых,; Similarity: 1.81114661693573
Text: Или кто сойдет в бездну? То есть Христа из мертвых возвести.; Similarity: 1.8135876655578613
```
</details>

<details>
<summary>Milvus similarity results on 814k dataset</summary>

```
Text: чтобы достигнуть воскресения мертвых.; Similarity: 0.9226888418197632
Text: Но Бог воскресил Его из мертвых.; Similarity: 0.8717797994613647
Text: Но Бог воскресил Его из мертвых.; Similarity: 0.8717797994613647
Text: а Начальника жизни убили. Сего Бог воскресил из мертвых, чему мы свидетели.; Similarity: 0.8707685470581055
Text: Но Христос воскрес из мертвых, первенец из умерших.; Similarity: 0.8627219796180725
Text: и что Он погребен был, и что воскрес в третий день, по Писанию,; Similarity: 0.8371096253395081
Text: Ибо как смерть через человека, так через человека и воскресение мертвых.; Similarity: 0.831940770149231
Text: которою Он воздействовал во Христе, воскресив Его из мертвых и посадив одесную Себя на небесах,; Similarity: 0.8282567262649536
Text: যীশু খ্রীষ্টকে স্মরণ করো, যিনি মৃতলোক থেকে পুনরুত্থিত হয়েছেন এবং যিনি দাউদের বংশজাত। এই হল আমার সুসমাচার।; Similarity: 0.827512264251709
Text: быв погребены с Ним в крещении, в Нем вы и совоскресли верою в силу Бога, Который воскресил Его из мертвых,; Similarity: 0.8162704110145569
```

</details>

### 4. Redis
Overall experience with Redis was ★★☆☆☆ (2/5).
✅ Redis is very fast for insertion
✅ As we use redis-stack, it came with redis-insight UI bundled. UI is nice, but not vector-specific. Can't see indexes or visualize embeddings.
🟡 API/Command syntax was not intuitive, had to spend too much time reverse-engineering it from docs and examples.
`redis.exceptions.ResponseError: Property vector_score not loaded nor in schema` while trying to search - index and query need to match
🟡 `unknown command 'JSON.SET'` while using `redis` image, likely related to JSON extension, had to switch to `redis-stack` image.
🟡for some reason ingestion took in only 21k rows instead of 24k
❌ Redis failed to ingest all rows (maybe I did some misconfiguration?).
  `redis.exceptions.BusyLoadingError: Redis is loading the dataset in memory` random error while loading dataset at 336K rows and 8.6GB of memory;
❌ Search was slow, even though it used an index
❌ `MISCONF Redis is configured to save RDB snapshots, but it's currently unable to persist to disk` while deleting keys



```bash
docker-compose -f docker-compose.redis.yml up
```

Docs:
https://redis-py.readthedocs.io/en/stable/examples/search_vector_similarity_examples.html

- <img width="600" alt="Screenshot 2024-08-21 at 16 19 02" src="https://github.com/user-attachments/assets/1c1c97c6-aba4-4282-bf06-f9e6dcdcd85e">

<details>
<summary>Redis similarity results on 21k dataset</summary>

```
Text: а Начальника жизни убили. Сего Бог воскресил из мертвых, чему мы свидетели.; Similarity: 0.87
Text: и что Он погребен был, и что воскрес в третий день, по Писанию,; Similarity: 0.84
Text: которою Он воздействовал во Христе, воскресив Его из мертвых и посадив одесную Себя на небесах,; Similarity: 0.83
Text: быв погребены с Ним в крещении, в Нем вы и совоскресли верою в силу Бога, Который воскресил Его из мертвых,; Similarity: 0.82
Text: Который предан за грехи наши и воскрес для оправдания нашего.; Similarity: 0.77
Text: Ибо Христос для того и умер, и воскрес, и ожил, чтобы владычествовать и над мертвыми и над живыми.; Similarity: 0.76
Text: ибо если мертвые не воскресают, то и Христос не воскрес.; Similarity: 0.76
Text: Царь Ирод, услышав об Иисусе, ибо имя Его стало гласно, говорил: это Иоанн Креститель воскрес из мертвых, и потому чудеса делаются им.; Similarity: 0.76
Text: вдруг, во мгновение ока, при последней трубе; ибо вострубит, и мертвые воскреснут нетленными, а мы изменимся.; Similarity: 0.76
Text: ныне примирил в теле Плоти Его, смертью Его, чтобы представить вас святыми и непорочными и неповинными пред Собою,; Similarity: 0.75
```

</details>

### Others

```bash
docker-compose -f docker-compose.weaviate.yml up weaviate
docker-compose -f docker-compose.chromadb.yml up
```

