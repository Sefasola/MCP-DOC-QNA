import os
from dotenv import load_dotenv
import sqlite3
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
import PyPDF2
from typing import Any

# .env içindeki değişkenleri (OPENAI_API_KEY, DB_PATH, DANGEROUSLY_OMIT_AUTH) yükle
load_dotenv()

# Durumsuz HTTP modu ve doğrudan JSON dönen cevaplar
mcp = FastMCP(
    "DocQnA",
    stateless_http=True,
    json_response=True
)

# OpenAI istemcisi
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SQLite veritabanı yolu
DB_PATH = os.getenv("DB_PATH", "data/docs.db")

def get_db():
    """SQLite bağlantısı açar ve satırları dict-like döner."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@mcp.resource("docs://list")
def list_docs() -> list[str]:
    """Veritabanındaki tüm doküman ID’lerini döner."""
    with get_db() as db:
        rows = db.execute("SELECT id FROM documents").fetchall()
    return [r["id"] for r in rows]

@mcp.tool("Load PDF")
def load_pdf(path: str) -> dict:
    """
    Verilen PDF dosyasını okuyup SQLite'a kaydeder.
    path: PDF dosyasının tam yolu
    """
    reader = PyPDF2.PdfReader(path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    doc_id = os.path.basename(path)
    with get_db() as db:
        db.execute(
            "INSERT OR REPLACE INTO documents (id, content) VALUES (?, ?)",
            (doc_id, text)
        )
        db.commit()
    return {"doc_id": doc_id, "status": "loaded"}

@mcp.tool("Ask Document")
def ask_document(doc_id: str, question: str) -> dict:
    """
    Daha önce yüklenmiş bir dokümana soruyu sorar, cevabı kaydeder ve döner.
    doc_id: documents tablosundaki id
    question: sorulacak metin
    """
    with get_db() as db:
        row = db.execute(
            "SELECT content FROM documents WHERE id = ?",
            (doc_id,)
        ).fetchone()
    content = row["content"] if row else ""

    prompt = f"Doküman:\n{content}\n\nSoru: {question}\nCevap:"
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content.strip()

    with get_db() as db:
        db.execute(
            "INSERT INTO questions (doc_id, question, answer) VALUES (?, ?, ?)",
            (doc_id, question, answer)
        )
        db.commit()

    return {"answer": answer}

# en alta, mevcut araçların hemen altına:
@mcp.resource("history://list")
def list_history() -> list[dict[str, Any]]:
    with get_db() as db:
        rows = db.execute(
            "SELECT id, doc_id, question, answer, asked_at FROM questions ORDER BY asked_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    # Streamable HTTP transport ile başlat; auth .env’de DANGEROUSLY_OMIT_AUTH=true ile atlanır
    mcp.run(transport="streamable-http")
