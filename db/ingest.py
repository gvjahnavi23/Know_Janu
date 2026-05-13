from db.vector_database import send_collection
from rag.embedder import embedder
from utils.helper import load_data

collection = send_collection()

data = load_data()

embeddings = embedder.encode(
    data['documents']
).tolist()

collection.add(
    ids=data['ids'],
    documents=data['documents'],
    metadatas=data['metadata'],
    embeddings=embeddings
)

print("Data inserted successfully")