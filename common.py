import sqlite3
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

# Function to fetch Bible text from the SQLite database and split it into sentences
def read_verses(handler, minibatch_size=100):
    db_path = 'bible.db'
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Initialize variables
    batch_size = 1000
    offset = 0
    sentences = []

    while True:
        # Query to select text from Chapter with LIMIT and OFFSET
        query = f'''
        SELECT ChapterVerse.text, translationId, bookId, chapterNumber, Number, embedding
        FROM ChapterVerse
        WHERE embedding IS NOT NULL
        ORDER BY ChapterVerse.chapterNumber, ChapterVerse.number
        LIMIT {batch_size} OFFSET {offset}
        '''

        # ChapterVerse.translationId = 'rus_syn' AND

        # Execute the query and fetch results
        cursor.execute(query)
        rows = cursor.fetchall()

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
            handler(chunk)

        # Increment the offset for the next batch
        offset += batch_size

    # Close the database connection
    conn.close()

    return sentences