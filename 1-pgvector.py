import sqlite3
import struct

import numpy as np
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
register_vector(postgres)
cur = postgres.cursor()

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')


# Function to fetch Bible text from the SQLite database and split it into sentences
def copy_embeddings():
    # Initialize variables
    batch_size = 100
    offset = 0

    # Connect to the SQLite database
    db_path = 'bible.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        while True:
            # Query to select text from Chapter with LIMIT and OFFSET
            query = f'''
            SELECT embedding, text
            FROM ChapterVerse
            WHERE ChapterVerse.embedding IS NOT NULL
            ORDER BY ChapterVerse.chapterNumber, ChapterVerse.number
            LIMIT {batch_size} OFFSET {offset}
            '''

            # Execute the query and fetch results
            cursor.execute(query)
            rows = cursor.fetchall()

            # If no more rows are returned, break the loop
            if not rows:
                break

            for row in rows:
                # Define the SQL INSERT query
                insert_query = """
                INSERT INTO store.embeddings (embedding, text)
                VALUES (%s, %s)
                """

                # Execute the INSERT query
                embedding = row[0]
                if isinstance(embedding, bytes):
                    embedding = list(struct.unpack(f'{len(embedding) // 4}f', embedding))

                cur.execute(insert_query, (embedding, row[1]))

                # Commit the transaction
                postgres.commit()


            # Increment the offset for the next batch
            offset += batch_size

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the database connection
        conn.close()

        # Close the cursor and connection
        if cur is not None:
            cur.close()
        if conn is not None:
            postgres.close()

def pgvector_search(text):
    embedding = model.encode(text)

    cur.execute(f"""
        SELECT text,  1 - (embedding <-> %s::vector) AS similarity
        FROM store.embeddings
        ORDER BY similarity desc
        LIMIT 10
    """, (embedding,))
    for r in cur.fetchall():
        # print(r)
        print(f"Text: {r[0]}; Similarity: {r[1]}")

copy_embeddings()
pgvector_search("воскресил из мертвых")