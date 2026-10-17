from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

def load_documents(directory: Path) -> list[Document]:
    if not directory.exists():
        raise FileNotFoundError(f"Documents directory does not exist: {directory}")
    docs: list[Document] = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            loaded = PyPDFLoader(str(path)).load()
        elif suffix in {".txt", ".md", ".markdown"}:
            loaded = TextLoader(str(path), encoding="utf-8").load()
        else:
            continue
        for doc in loaded:
            doc.metadata["source"] = str(path)
            doc.metadata.setdefault("file_name", path.name)
        docs.extend(loaded)
    if not docs:
        raise ValueError(f"No supported PDF/TXT/Markdown documents found in {directory}")
    return docs
