from pathlib import Path
from typing import List


def save_uploaded_files(files: List[bytes], filenames: List[str], upload_dir: Path) -> List[Path]:
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: List[Path] = []
    for content, name in zip(files, filenames):
        file_path = upload_dir / name
        file_path.write_bytes(content)
        saved_paths.append(file_path)
    return saved_paths


def extract_text_from_files(file_paths: List[Path]) -> str:
    # Placeholder extractor. Replace with PDF/Docx parsers later.
    snippets = [f"[Extracted text from {path.name}]" for path in file_paths]
    return "\n".join(snippets)
