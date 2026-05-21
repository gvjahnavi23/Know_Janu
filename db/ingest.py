from db.vector_database import send_collection
from rag.embedder import embedder
from utils.helper import load_data

collection = send_collection()

data = load_data()

documents = [
    item["document"]
    for item in data
]

ids = [
    item["id"]
    for item in data
]

metadatas = []

for item in data:

    normalized_metadata = {}

    for key, value in item["metadata"].items():

        if isinstance(value, str):

            normalized_metadata[key] = (
                value.lower()
            )

        else:

            normalized_metadata[key] = value

    metadatas.append(
        normalized_metadata
    )

embeddings = embedder.encode(
    documents
).tolist()

collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
    embeddings=embeddings
)

print("Data inserted successfully")