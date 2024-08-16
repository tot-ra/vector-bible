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
        SELECT translationId || bookId || '-' || chapterNumber || '-' || Number AS id, ChapterVerse.text
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
            handler(row[0], row[1])

        # Increment the offset for the next batch
        offset += batch_size

    # Close the database connection
    conn.close()

    return sentences