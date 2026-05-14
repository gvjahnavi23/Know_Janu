from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(self, documents):

        self.documents = documents

        self.tokenized_docs = [
            doc.lower().split()
            for doc in documents
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_docs
        )

    def retrieve(
        self,
        query,
        top_k=4
    ):

        tokenized_query = (
            query.lower().split()
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = (
            scores.argsort()[::-1][:top_k]
        )

        results = []

        for idx in ranked_indices:

            results.append({
                "document": self.documents[idx],
                "score": float(scores[idx]),
                "source": "bm25"
            })

        return results