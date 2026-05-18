from sentence_transformers import CrossEncoder

from utils.config import (
    RERANKER_MODEL,
    TOP_K_RERANK
)


class Reranker:

    def __init__(self):

        self.model = CrossEncoder(
            RERANKER_MODEL
        )

    def rerank(
        self,
        query,
        documents,
        top_k = TOP_K_RERANK
    ):
        pairs = [
            (query, doc)
            for doc in documents
        ]

        scores = (
            self.model.predict(pairs)
        )

        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:top_k]