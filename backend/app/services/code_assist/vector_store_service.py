import faiss
import numpy as np
import pickle
from pathlib import Path

BASE_INDEX_DIR = Path("data/vector_index")


def get_index_path(repo_id: str):
    return BASE_INDEX_DIR / repo_id


# -------------------------
# STORE INDEX
# -------------------------
def store_embeddings(repo_id: str, items):
    index_dir = get_index_path(repo_id)
    index_dir.mkdir(parents=True, exist_ok=True)

    valid_embeddings = [
        item["embedding"]
        for item in items
        if isinstance(item.get("embedding"), list) and len(item["embedding"]) == 768
    ]   

    if not valid_embeddings:
        raise ValueError("No valid embeddings generated.")

    vectors = np.array(valid_embeddings).astype("float32")

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    faiss.write_index(index, str(index_dir / "index.faiss"))

    with open(index_dir / "metadata.pkl", "wb") as f:
        pickle.dump(items, f)


# -------------------------
# LOAD INDEX  ← THIS WAS MISSING
# -------------------------
def load_index(repo_id: str):
    index_dir = get_index_path(repo_id)

    index_path = index_dir / "index.faiss"
    metadata_path = index_dir / "metadata.pkl"

    if not index_path.exists():
        raise FileNotFoundError(f"No FAISS index found for repo '{repo_id}'")

    index = faiss.read_index(str(index_path))

    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata