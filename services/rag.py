import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI

from services.parser import extract_text
from services.guardrails import guardrail_response

# -------- MODELS --------
model = SentenceTransformer('all-MiniLM-L6-v2')


client = OpenAI(api_key=" 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")  # <-- paste WITHOUT space

chunks = []
index = None


# ---------- CHUNKING ----------
def chunk_text(text, size=500, overlap=100):
    result = []
    for i in range(0, len(text), size - overlap):
        result.append(text[i:i+size])
    return result


# ---------- LOAD DOCUMENTS ----------
def load_documents(file_list):
    global chunks, index

    all_chunks = []

    for file in file_list:
        file_name = file["name"]

        text = extract_text(file)
        chunked = chunk_text(text)

        for c in chunked:
            all_chunks.append({
                "text": c,
                "file": file_name
            })

    if not all_chunks:
        raise Exception("No content extracted")

    chunks = all_chunks

    texts = [c["text"] for c in chunks]

    # 🔥 IMPORTANT FIX (dtype)
    embeddings = model.encode(texts)
    embeddings = np.array(embeddings).astype("float32")

    dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    print("✅ Documents indexed:", len(chunks))


# ---------- ASK ----------
def ask_question(question):
    global index, chunks

    if index is None or not chunks:
        return {
            "answer": "❌ Documents not loaded",
            "sources": []
        }

    try:
        # -------- EMBED QUERY --------
        q_emb = model.encode([question])
        q_emb = np.array(q_emb).astype("float32")

        D, I = index.search(q_emb, k=3)

        # -------- GUARDRAILS --------
        valid, message = guardrail_response(D)

        if not valid:
            return {
                "answer": message,
                "sources": []
            }

        retrieved_chunks = []
        sources = set()

        for i in I[0]:
            retrieved_chunks.append(chunks[i]["text"])
            sources.add(chunks[i]["file"])

        context = "\n".join(retrieved_chunks)

        print("🔍 Context used:", context[:200])

    
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Answer ONLY using the provided context. If answer not present, say 'Not found in documents'."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}"
                }
            ],
            temperature=0.2
        )

        print("✅ RAW RESPONSE:", response)

        answer = response.choices[0].message.content

        if not answer:
            answer = "❌ Empty response from model"

        return {
            "answer": answer,
            "sources": list(sources)
        }

    except Exception as e:
        print("🔥 ERROR:", str(e))  # VERY IMPORTANT

        return {
            "answer": f"❌ Error: {str(e)}",
            "sources": []
        }