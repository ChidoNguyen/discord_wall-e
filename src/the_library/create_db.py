import sqlite3

DB_PATH = "epub_index.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

##Create Table##
cursor.execute('''
    CREATE TABLE IF NOT EXISTS digital_brain (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        file_name TEXT NOT NULL,
        user TEXT NOT NULL
    )
''')
cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON digital_brain(title)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_author ON digital_brain(author)")
conn.commit()
conn.close()
print(f'Database {DB_PATH} created.')