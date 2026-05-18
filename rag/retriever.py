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
        if not results["documents"]:
            return []

        documents = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]
        ids = results["ids"][0]

        retrieved = []

        for doc, score, metadata, doc_id in zip(
            documents,
            distances,
            metadatas,
            ids
        ):

            retrieved.append({
                "id": doc_id,
                "document": doc,
                "metadata": metadata,
                "score": 1 - float(score),
                "source": "dense"
            })

        return retrieved