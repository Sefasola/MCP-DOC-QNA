import sqlite3

conn = sqlite3.connect("data/docs.db")
c = conn.cursor()

# Doküman tablosu
c.execute("""
  CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
""")

# Soru-cevap geçmişi tablosu
c.execute("""
  CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(doc_id) REFERENCES documents(id)
  )
""")

conn.commit()
conn.close()
