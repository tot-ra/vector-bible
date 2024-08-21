import sqlite3
from sentence_transformers import SentenceTransformer
import psycopg2
from pgvector.psycopg2 import register_vector

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

conn_params = {
    'dbname': 'store',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# Function to fetch Bible text from the SQLite database and split it into sentences
def read_verses(handler, max_items = 24000, minibatch_size=100):
    # Connect to the PostgreSQL database
    postgres = psycopg2.connect(**conn_params)
    cur = postgres.cursor()

    cur.execute("SET search_path TO store, public")
    register_vector(cur)

    # Initialize variables
    batch_size = 1000
    offset = 0
    sentences = []

    elapsed_time = 0
    calls = 0

    # AND translationId = 'rus_syn'
    while offset < max_items:
        # Query to select text from Chapter with LIMIT and OFFSET
        query = f'''
        SELECT text, translationId, bookId, chapterNumber, Number, embedding
        FROM store."ChapterVerse"
        WHERE embedding IS NOT NULL AND translationId = 'rus_syn'
        ORDER BY chapterNumber, number
        LIMIT {batch_size} OFFSET {offset}
        '''

        # Execute the query and fetch results
        cur.execute(query)
        rows = cur.fetchall()

        # If no more rows are returned, break the loop
        if not rows:
            break

        preprocessedRows = []
        for row in rows:
            id = f'{row[1]}_{row[2]}_{row[3]}_{row[4]}'
            text = row[0]
            meta = {'translationId': row[1], 'bookId': row[2], 'chapterNumber': row[3], 'verseNumber': row[4]}
            embedding = row[5]
            preprocessedRows.append((id, text, meta, embedding))

        for i in range(0, len(preprocessedRows), minibatch_size):
            chunk = preprocessedRows[i:i + minibatch_size]
            calls += 1
            elapsed_time += handler(chunk)

        # Increment the offset for the next batch
        offset += batch_size

    print(f"avg insert time: {elapsed_time/calls} sec")

    # Close the database connection
    cur.close()

    return sentences