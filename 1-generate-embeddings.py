import sqlite3
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

# Function to fetch Bible text from the SQLite database and split it into sentences
def generate_embeddings():
    db_path = 'bible.db'
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Initialize variables
    batch_size = 1000
    offset = 0

    while True:
        # Query to select text from Chapter with LIMIT and OFFSET
        query = f'''
        SELECT ChapterVerse.text, translationId, bookId, chapterNumber, Number
        FROM ChapterVerse
        WHERE ChapterVerse.embedding IS NULL
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
            text = row[0]
            embeddings = model.encode(text)
            cursor.execute(f'''
                UPDATE ChapterVerse
                SET embedding = ?
                WHERE translationId = ? AND bookId = ? AND chapterNumber = ? AND Number = ?
                ''', (embeddings, row[1], row[2], row[3], row[4]))
            print(text)
            conn.commit()


        # Increment the offset for the next batch
        offset += batch_size

    # Close the database connection
    conn.close()

generate_embeddings()