from utils.helper import load_data

from rag.router import category_filter
from rag.bm25_retriever import BM25Retriever
from rag.retriever import DenseRetriever
from rag.fusion import reciprocal_rank_fusion
from rag.reranker import Reranker
from rag.prompt_builder import prompt_builder
from rag.generator import generator


class HybridRAGPipeline:

    def __init__(self):

        data = load_data()

        self.documents = data["documents"]

        self.bm25 = BM25Retriever(
            self.documents
        )

        self.dense = DenseRetriever()

        self.reranker = Reranker()

    def retrieve_context(
        self,
        query
    ):

        where_filter = (
            category_filter(query)
        )

        bm25_results = (
            self.bm25.retrieve(query)
        )

        dense_results = (
            self.dense.retrieve(
                query,
                where_filter[0]
            )
        )

        fused_results = (
            reciprocal_rank_fusion(
                bm25_results,
                dense_results
            )
        )

        fused_documents = [
            item["document"]
            for item in fused_results
        ]

        reranked = (
            self.reranker.rerank(
                query,
                fused_documents
            )
        )

        final_docs = [
            doc
            for doc, score in reranked
        ]

        return "\n\n".join(final_docs)

    def ask(self, query):

        context = self.retrieve_context(
            query
        )

        prompt = prompt_builder(
            query,
            context
        )

        return generator(prompt)