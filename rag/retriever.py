from db.vector_database import send_collection
from rag.embedder import embedder
from utils.config import TOP_K_DENSE


class DenseRetriever:

    def __init__(self):

        self.collection = send_collection()

    def retrieve(
        self,
        query,
        where_filter=None,
        top_k=TOP_K_DENSE
    ):

        query_embedding = (
            embedder.encode(query)
            .tolist()
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )

        documents = (
            results["documents"][0]
        )

        distances = (
            results["distances"][0]
        )

        retrieved = []

        for doc, score in zip(
            documents,
            distances
        ):

            retrieved.append({
                "document": doc,
                "score": float(score),
                "source": "dense"
            })

        return retrieved