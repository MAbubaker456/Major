from backend.app.core.ollama_client import embed

def embed_chunks(chunks):
    enriched = []

    for chunk in chunks:
        text = chunk["text"].strip()

        # Skip empty chunks
        if not text:
            continue

        vector = embed(text)

        # Skip invalid embeddings
        if not isinstance(vector, list) or len(vector) != 768:
            print("Skipping invalid embedding")
            continue

        chunk["embedding"] = vector
        enriched.append(chunk)

    return enriched