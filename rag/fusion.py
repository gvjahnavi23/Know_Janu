def reciprocal_rank_fusion(
    bm25_results,
    dense_results,
    k=60
):

    scores = {}

    documents = {}

    combined_results = (
        bm25_results
        + dense_results
    )

    for rank, item in enumerate(
        combined_results
    ):

        doc_id = item["id"]

        rrf_score = (
            1 / (k + rank + 1)
        )

        scores[doc_id] = (

            scores.get(doc_id, 0)

            + rrf_score
        )

        documents[doc_id] = item

    reranked = sorted(

        scores.items(),

        key=lambda x: x[1],

        reverse=True
    )

    fused_results = []

    for doc_id, score in reranked:

        item = documents[doc_id]

        item["score"] = score

        fused_results.append(item)

    return fused_results