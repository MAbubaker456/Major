from pathlib import Path
from backend.app.services.repo_fetcher import get_repo_directory, load_repo_manifest
from .chunking_service import chunk_file
from .embedding_service import embed_chunks
from .vector_store_service import store_embeddings


def ingest_repository(repo_id: str):
    repo_dir = get_repo_directory(repo_id)
    manifest = load_repo_manifest(repo_id)

    all_chunks = []

    for file in manifest["files"]:
        path = repo_dir / file["path"]

        if not path.exists():
            continue

        if path.suffix.lower() in {".py", ".js", ".ts", ".java"}:
            chunks = chunk_file(path)

            for chunk in chunks:
                chunk["file_path"] = file["path"]
                chunk["risk_level"] = file.get("risk_level", "low")
                all_chunks.append(chunk)

    embeddings = embed_chunks(all_chunks)

    store_embeddings(repo_id, embeddings)

    return {"status": "indexed", "chunks": len(all_chunks)}