from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(
        self,
        documents
    ):

        self.documents = documents

        self.tokenized_docs = [

            doc["document"]
            .lower()
            .split()

            for doc in documents
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_docs
        )

    def retrieve(
        self,
        query,
        where_filter=None,
        top_k=4
    ):

        tokenized_query = (

            query
            .lower()
            .split()
        )

        scores = (
            self.bm25.get_scores(
                tokenized_query
            )
        )

        ranked_indices = (
            scores.argsort()[::-1]
        )

        results = []

        for idx in ranked_indices:

            doc = self.documents[idx]

            if where_filter:

                matched = True

                for key, value in (
                    where_filter.items()
                ):

                    if (
                        doc["metadata"]
                        .get(key)
                        != value
                    ):

                        matched = False
                        break

                if not matched:
                    continue

            results.append({

                "id":
                doc["id"],

                "document":
                doc["document"],

                "metadata":
                doc["metadata"],

                "score":
                float(scores[idx]),

                "source":
                "bm25"
            })

            if len(results) >= top_k:
                break

        return results