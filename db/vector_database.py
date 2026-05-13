from pathlib import Path
import chromadb

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "db" / "chroma_db"

client = chromadb.PersistentClient(
    path=str(DB_PATH)
)

def send_collection():
    return client.get_or_create_collection(
        name="vectors"
    )