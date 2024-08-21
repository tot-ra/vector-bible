import sqlite3
import struct
import time
import psycopg2
from pgvector.psycopg2 import register_vector

from sentence_transformers import SentenceTransformer

conn_params = {
    'dbname': 'store',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# Connect to the PostgreSQL database
postgres = psycopg2.connect(**conn_params)
cur = postgres.cursor()

cur.execute("SET search_path TO store, public")
register_vector(cur)

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')


# Function to fetch Bible text from the SQLite database and split it into sentences
def generate_embeddings():
    # Initialize variables
    batch_size = 1000
    offset = 0

    try:
        while True:
            # Query to select text from Chapter with LIMIT and OFFSET
            query = f'''
            SELECT text, translationId, bookId, chapterNumber, Number
            FROM store."ChapterVerse"
            WHERE embedding IS NULL
            ORDER BY chapterNumber, number
            LIMIT {batch_size} OFFSET {offset}
            '''

            # AND translationId = 'rus_syn'

            # Execute the query and fetch results
            cur.execute(query)
            rows = cur.fetchall()

            # If no more rows are returned, break the loop
            if not rows:
                break

            for row in rows:
                text = row[0]
                # print(text)
                embeddings = model.encode(text)
                cur.execute(f'''
                    UPDATE store."ChapterVerse"
                    SET embedding = %s
                    WHERE translationId = %s AND bookId = %s AND chapterNumber = %s AND Number = %s
                    ''', (embeddings, row[1], row[2], row[3], row[4]))

                # Commit the transaction
                postgres.commit()


            # Increment the offset for the next batch
            offset += batch_size

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        if cur is not None:
            cur.close()

        # Close the database connection
        postgres.close()

def pgvector_search(text):
    embedding = model.encode(text)

    cur.execute(f'''
        SELECT text,  1 - (embedding <=> %s::store.vector) AS similarity
        FROM store."ChapterVerse"
        WHERE translationId = 'rus_syn' AND embedding IS NOT NULL
        ORDER BY similarity desc
        LIMIT 10;
    ''', (embedding,))
    for r in cur.fetchall():
        # print(r)
        print(f"Text: {r[0]}; Similarity: {r[1]}")

# generate_embeddings()

start_time = time.perf_counter()

pgvector_search("воскресил из мертвых")
pgvector_search("воскресил из мертвых")
pgvector_search("воскресил из мертвых")
pgvector_search("воскресил из мертвых")
pgvector_search("воскресил из мертвых")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Search time: {elapsed_time/5} sec")