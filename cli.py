import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag.chain import build_rag_chain
from src.kuesioner.data import load_kuesioner, get_profile
import uuid


def kuesioner():
    data = load_kuesioner()
    total = 0

    print("=" * 60)
    print("  KUESIONER PROFIL RISIKO INVESTASI")
    print("=" * 60)
    print()

    for i, q in enumerate(data["questions"], 1):
        print(f"[{i}] {q['text']}")
        for j, opt in enumerate(q["options"], 1):
            print(f"     {j}. {opt['text']}")
        while True:
            try:
                pilih = int(input("  Pilih (1-4): "))
                if 1 <= pilih <= 4:
                    total += q["options"][pilih - 1]["score"]
                    break
            except ValueError:
                pass
            print("  Pilihan tidak valid, coba lagi.")
        print()

    profil = get_profile(data["profiles"], total)
    print("-" * 60)
    print(f"  TOTAL SKOR: {total}")
    print(f"  PROFIL RISIKO ANDA: {profil['name']}")
    print(f"  Deskripsi: {profil.get('description', '')}")
    print()

    print("  Alokasi produk yang sesuai:")
    for cat, alokasi in profil["allocation"].items():
        produk = ", ".join(data["product_categories"].get(cat, []))
        print(f"    {cat} ({alokasi}): {produk}")
    print("-" * 60)
    print()
    return profil


rag = build_rag_chain()
session_id = str(uuid.uuid4())

profil = kuesioner()

print("[AI] Asisten Pasar Modal (CLI)")
print("Ketik 'exit' untuk keluar\n")

while True:
    prompt = input("Tanya: ")
    if prompt.lower() == "exit":
        break

    result = rag["chain"].invoke(
        {"input": prompt},
        config={"configurable": {"session_id": session_id}},
    )

    answer = result["answer"]
    contexts = result.get("context", [])

    if contexts:
        print(f"\n[Konteks] ({len(contexts)} chunks):")

    print(f"\nJawab: {answer}\n")
