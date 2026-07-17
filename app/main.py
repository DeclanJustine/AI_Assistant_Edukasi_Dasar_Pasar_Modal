import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import uuid
from src.rag_chain import build_rag_chain
from src.history import clear_session

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

st.set_page_config(page_title="Asisten Pasar Modal", page_icon="📈", layout="wide")
st.title("📈 Asisten Edukasi Pasar Modal")
st.caption("Tanyakan apa saja tentang investasi dan pasar modal Indonesia")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "rag" not in st.session_state:
    with st.spinner("Memuat model AI..."):
        st.session_state.rag = build_rag_chain()
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Pengaturan")
    if st.button("🗑️ Hapus Riwayat Percakapan"):
        clear_session(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    st.divider()
    st.markdown("**Sumber Data:**")
    st.markdown("- Dokumen PDF tentang pasar modal")
    st.markdown("- Artikel dari OJK (sikapiuangmu.ojk.go.id)")
    st.divider()
    st.caption("Dibuat dengan LangChain + Ollama")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tanyakan tentang pasar modal..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Mencari informasi..."):
            result = st.session_state.rag["chain"].invoke(
                {"input": prompt},
                config={"configurable": {"session_id": st.session_state.session_id}},
            )
            answer = result["answer"]
            contexts = result.get("context", [])
            context_text = "\n".join(doc.page_content for doc in contexts)

        with st.spinner("Memverifikasi jawaban..."):
            llm = st.session_state.rag["llm"]
            verify_input = VERIFY_PROMPT.format(
                context=context_text,
                answer=answer,
                question=prompt,
            )
            verify_result = llm.invoke(verify_input).content.strip().upper()

            if "YA" not in verify_result:
                answer = "Maaf, informasi tidak tersedia pada referensi"

        st.markdown(answer)

        if contexts:
            with st.expander("📄 Sumber referensi"):
                for i, doc in enumerate(contexts, 1):
                    source = doc.metadata.get("source", "Unknown")
                    st.markdown(f"**{i}.** [{source}]({source})")

    st.session_state.messages.append({"role": "assistant", "content": answer})
