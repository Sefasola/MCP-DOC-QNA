#!/usr/bin/env python3
import os
import json
import asyncio
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# 1. Ortam değişkenlerini yükle (.env içinden OPENAI_API_KEY ve MCP_SERVER_URL alınır)
load_dotenv()

# 2. MCP sunucu URL'sini .env ya da default olarak al
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

async def main():
    # 3. Streamable HTTP transport ile MCP sunucusuna bağlan
    async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 4. PDF yükleme
            pdf_path = "Example.pdf"  # Proje köküne kopyaladığınız dosya
            load_result = await session.call_tool(
                "Load PDF",
                {"path": pdf_path}
            )
            print("PDF yükleme sonucu:", load_result)
            if load_result.isError:
                print("PDF yüklenirken hata oluştu, çıkılıyor.")
                return

            # 5. Doküman listesini oku
            list_result = await session.read_resource("docs://list")
            raw_list = list_result.contents[0].text
            docs = json.loads(raw_list)
            print("Mevcut dokümanlar:", docs)
            if not docs:
                print("Yüklü doküman bulunamadı, çıkılıyor.")
                return

            # 6. İlk dokümana soru sor
            doc_id = docs[0]
            ask_result = await session.call_tool(
                "Ask Document",
                {"doc_id": doc_id, "question": "Özetler misin?"}
            )
            # JSON parse
            answer_data = json.loads(ask_result.content[0].text)
            answer = answer_data.get("answer", "[Cevap alınamadı]")
            print(f"\n‘{doc_id}’ için model cevabı:\n{answer}")

            # 7. Sorgu geçmişini çek ve yazdır
            history_result = await session.read_resource("history://list")
            raw_history = history_result.contents[0].text
            history = json.loads(raw_history)
            print("\n--- Sorgu Geçmişi ---")
            for entry in history:
                ts = entry.get("asked_at")
                q  = entry.get("question")
                a  = entry.get("answer")
                print(f"[{ts}] {q} → {a}")

if __name__ == "__main__":
    asyncio.run(main())
