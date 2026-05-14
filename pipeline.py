from utils.config import TOP_K_RERANK

from utils.helper import (
    load_data,
    follow_up,
    query_type
)

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

        self.state = {
            "last_category": None,
            "last_topic": None,
            "last_results": None,
            "chat_history": []
        }
        self.type_of_query = None

    def retrieve_context(
        self,
        query
    ):

        # -----------------------------
        # Follow-up query detection
        # -----------------------------

        is_follow_up = any(
            phrase in query.lower()
            for phrase in follow_up()
        )

        # -----------------------------
        # Dynamic retrieval size
        # -----------------------------

        self.type_of_query = query_type(query)

        top_k = TOP_K_RERANK

        if self.type_of_query == "broad":
            top_k = 9

        # -----------------------------
        # Category routing
        # -----------------------------

        where_filter = category_filter(query)

        # -----------------------------
        # Reuse previous category
        # for follow-up queries
        # -----------------------------

        if (
            not where_filter
            and is_follow_up
            and self.state["last_category"]
        ):

            where_filter = (
                self.state["last_category"]
            )

        # -----------------------------
        # Default fallback
        # -----------------------------

        if not where_filter:

            where_filter = {
                "category": "profile"
            }


        # -----------------------------
        # BM25 Retrieval
        # -----------------------------

        bm25_results = (
            self.bm25.retrieve(query)
        )


        # -----------------------------
        # Dense Retrieval
        # -----------------------------

        dense_results = (
            self.dense.retrieve(
                query,
                where_filter
            )
        )


        # -----------------------------
        # Store conversation state
        # -----------------------------

        if dense_results:

            top_result = dense_results[0]

            self.state["last_category"] = (
                where_filter
            )

            self.state["last_topic"] = (
                top_result["id"]
            )

            self.state["last_results"] = (
                dense_results
            )

        # -----------------------------
        # Fusion
        # -----------------------------

        fused_results = (
            reciprocal_rank_fusion(
                bm25_results,
                dense_results
            )
        )

        # -----------------------------
        # Preserve full retrieval objects
        # -----------------------------
        fused_documents = [
            item["document"]
            for item in fused_results
        ]

        # -----------------------------
        # Reranking
        # -----------------------------

        if self.type_of_query == "broad":
            final_docs = fused_documents[:6]
        else:
            reranked = (
                self.reranker.rerank(
                    query,
                    fused_documents,
                    top_k=top_k
                )
        )

        # -----------------------------
        # Final Context
        # -----------------------------

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
            context,
            self.type_of_query
        )

        response = generator(prompt)

        # -----------------------------
        # Store chat history
        # -----------------------------

        self.state["chat_history"].append({
            "role": "user",
            "content": query
        })

        self.state["chat_history"].append({
            "role": "assistant",
            "content": response
        })

        return response