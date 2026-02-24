from .vector_store_service import load_index
from backend.app.core.ollama_client import generate, embed
import numpy as np


def ask_question(repo_id: str, question: str):
    index, metadata = load_index(repo_id)

    query_vector = embed(question)
    distances, indices = index.search(
        np.array([query_vector]).astype("float32"), 5
    )

    retrieved = [metadata[i] for i in indices[0]]

    context = "\n\n".join([item["text"] for item in retrieved])

    prompt = f"""
You are a senior software engineer helping a beginner understand a codebase.

Context:
{context}

Question:
{question}

Explain clearly and precisely.
"""

    response = generate("deepseek-coder:6.7b", prompt)

    return {
        "answer": response,
        "sources": [r["file_path"] for r in retrieved]
    }