from pathlib import Path

def chunk_file(file_path: Path, max_lines: int = 120):
    content = file_path.read_text(errors="ignore")
    lines = content.split("\n")

    chunks = []
    for i in range(0, len(lines), max_lines):
        chunk_text = "\n".join(lines[i:i + max_lines])
        chunks.append({
            "text": chunk_text,
            "start_line": i + 1,
            "end_line": min(i + max_lines, len(lines))
        })

    return chunks