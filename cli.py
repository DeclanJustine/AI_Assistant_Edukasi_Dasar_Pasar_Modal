import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_chain import build_rag_chain
import uuid

VERIFY_PROMPT = """Tugas Anda: Tentukan apakah jawaban di bawah DIDUKUNG PENUH oleh konteks dokumen.

KONTEKS DOKUMEN:
{context}

PERTANYAAN: {question}

JAWABAN:
{answer}

Aturan penilaian:
1. Jika jawaban mengutip informasi dari LUAR konteks (buku, sumber eksternal, pengetahuan umum), jawab: TIDAK
2. Jika jawaban menyatakan "tidak ada", "tidak tersedia", "tidak eksplisit" tentang hal yang ditanyakan, jawab: TIDAK
3. Jika jawaban menambahkan informasi yang TIDAK ada di konteks, meskipun ada bagian yang benar, jawab: TIDAK
4. Jika jawaban SEPENUHNYA didukung oleh konteks dokumen, jawab: YA

Pertanyaan utama adalah: "{question}"
Apakah jawaban memberikan informasi tentang "{question}" yang BENAR-BENAR ada di konteks?

Jawab HANYA dengan YA atau TIDAK."""

rag = build_rag_chain()
session_id = str(uuid.uuid4())

print("📈 Asisten Pasar Modal (CLI)")
print("Ketik 'exit' untuk keluar\n")

while True:
    prompt = input("❓ Tanya: ")
    if prompt.lower() == "exit":
        break

    result = rag["chain"].invoke(
        {"input": prompt},
        config={"configurable": {"session_id": session_id}},
    )

    answer = result["answer"]
    contexts = result.get("context", [])
    context_text = "\n".join(d.page_content for d in contexts)

    if contexts:
        print(f"\n📄 Konteks ({len(contexts)} chunks):")
        for i, doc in enumerate(contexts[:10], 1):
            print(f"   [{i}] {doc.page_content[:150]}...")

    llm = rag["llm"]
    v = llm.invoke(VERIFY_PROMPT.format(
        context=context_text, answer=answer, question=prompt,
    )).content.strip().upper()

    if "YA" not in v:
        answer = "Maaf, informasi tidak tersedia pada referensi"

    print(f"\n💡 {answer}\n")
