from sentence_transformers import CrossEncoder

from rag.retriever import retriever

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

def rerank(query):
    contexts = retriever(query)
    pairs = [
        (query, context)
        for context in contexts
    ]
    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(contexts, scores),
        key=lambda x: x[1],
        reverse=True
    )
    print(ranked)
    context = "\n\n".join([
        doc.strip()
        for doc, score in ranked[:2]
    ])
    return context