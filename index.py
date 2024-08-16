import sqlite3

# Function to fetch Bible text from the SQLite database and split it into sentences
def scripture(handler):
    db_path = 'bible.db'
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Initialize variables
    batch_size = 100
    offset = 0
    sentences = []

    while True:
        # Query to select text from Chapter with LIMIT and OFFSET
        query = f'''
        SELECT ChapterVerse.text, translationId, bookId, chapterNumber, Number
        FROM ChapterVerse
        WHERE ChapterVerse.translationId = 'rus_syn'
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
            id = f'{row[1]}_{row[2]}_{row[3]}_{row[4]}'
            text = row[0]
            meta = {'translationId': row[1], 'bookId': row[2], 'chapterNumber': row[3], 'verseNumber': row[4]}
            handler(id, text, meta)

        # Increment the offset for the next batch
        offset += batch_size

    # Close the database connection
    conn.close()

    return sentences