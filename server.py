import os
import sqlite3
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
import PyPDF2

# MCP ve OpenAI istemcileri
mcp = FastMCP("DocQnA")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_PATH = "data/docs.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@mcp.resource("docs://list")
def list_docs() -> list[str]:
    """Yüklü doküman kimliklerini döner."""
    with get_db() as db:
        rows = db.execute("SELECT id FROM documents").fetchall()
    return [r["id"] for r in rows]

@mcp.tool("Load PDF")
def load_pdf(path: str) -> dict:
    """PDF dosyasını okuyup veritabanına ekler."""
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
    """Belirtilen dokümana soruyu sorup yanıt döner ve kaydeder."""
    with get_db() as db:
        row = db.execute(
            "SELECT content FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()
    content = row["content"] if row else ""
    prompt = f"Doküman:\n{content}\n\nSoru: {question}\nCevap:"
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content": prompt}]
    )
    answer = response.choices[0].message.content
    with get_db() as db:
        db.execute(
            "INSERT INTO questions (doc_id, question, answer) VALUES (?, ?, ?)",
            (doc_id, question, answer)
        )
        db.commit()
    return {"answer": answer}

if __name__ == "__main__":
    mcp.run()
