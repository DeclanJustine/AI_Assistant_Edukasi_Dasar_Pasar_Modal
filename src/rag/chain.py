from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory

from config import LLM_MODEL
from src.rag.store import get_retriever
from src.rag.prompts import qa_prompt, history_rewriter_prompt
from src.rag.history import get_session_history

NORMALISASI_INPUT = {
    "reksadana": "reksa dana",
}


def get_llm():
    return ChatOllama(model=LLM_MODEL, temperature=0.0, max_tokens=250)


def normalisasi(query: str) -> str:
    q = query.lower()
    for k, v in NORMALISASI_INPUT.items():
        q = q.replace(k, v)
    return q


def build_rag_chain():
    llm = get_llm()
    retriever = get_retriever()

    history_aware_retriever = create_history_aware_retriever(
        llm=llm,
        retriever=retriever,
        prompt=history_rewriter_prompt,
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    class NormalizedChain:
        def __init__(self, chain):
            self._chain = chain

        def invoke(self, inputs, config=None, **kwargs):
            inputs["input"] = normalisasi(inputs.get("input", ""))
            return self._chain.invoke(inputs, config, **kwargs)

    return {"chain": NormalizedChain(chain), "llm": llm}
