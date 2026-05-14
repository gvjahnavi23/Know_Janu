def reciprocal_rank_fusion(
    bm25_results,
    dense_results,
    k=60
):

    scores = {}

    all_results = [
        bm25_results,
        dense_results
    ]

    for result_list in all_results:

        for rank, item in enumerate(
            result_list
        ):

            doc = item["document"]

            rrf_score = 1 / (
                k + rank + 1
            )

            if doc not in scores:
                scores[doc] = 0

            scores[doc] += rrf_score

    fused = []

    for doc, score in scores.items():

        fused.append({
            "document": doc,
            "score": score
        })

    fused = sorted(
        fused,
        key=lambda x: x["score"],
        reverse=True
    )

    return fused