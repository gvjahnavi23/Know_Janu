from utils.helper import load_data
from rag.router import category_filter
from rag.query_processor import QueryProcessor
from rag.bm25_retriever import BM25Retriever
from rag.retriever import DenseRetriever
from rag.fusion import reciprocal_rank_fusion
from rag.reranker import  Reranker
from rag.prompt_builder import prompt_builder
from rag.generator import generator


class HybridRAGPipeline:

    def __init__(self):

        data = load_data()

        self.documents = data

        self.bm25 = BM25Retriever(
            self.documents
        )

        self.dense = DenseRetriever()

        self.reranker = Reranker()

        self.query_processor = (
            QueryProcessor(
                self.documents
            )
        )

        self.state = {

            "active_entity": None,

            "last_project": None,

            "last_skill": None,

            "last_organization": None,

            "last_education": None,

            "last_query": None,

            "chat_history": []
        }

    def build_entity_filter(self):

        where_filter = {}

        active_entity = (
            self.state["active_entity"]
        )

        if not active_entity:

            return where_filter

        entity_type = (
            active_entity["type"]
        )

        entity_value = (
            active_entity["value"]
        )

        if entity_type == "project":

            where_filter[
                "project"
            ] = entity_value

        elif entity_type == "organization":

            where_filter[
                "organization"
            ] = entity_value

        elif entity_type == "skill":

            where_filter[
                "skill"
            ] = entity_value

        elif entity_type == "education":

            where_filter[
                "institution"
            ] = entity_value

        return where_filter

    def apply_entity_diversity(
        self,
        results
    ):

        unique_entities = set()

        filtered_results = []

        for item in results:

            metadata = (
                item["metadata"]
            )

            entity = (

                metadata.get("project")

                or metadata.get("skill")

                or metadata.get(
                    "organization"
                )

                or metadata.get(
                    "institution"
                )

                or item.get("id")
            )

            if not entity:

                entity = (
                    item["document"][:50]
                )

            if entity not in unique_entities:

                unique_entities.add(
                    entity
                )

                filtered_results.append(
                    item
                )

        return filtered_results

    def map_reranked_results(
        self,
        reranked_docs,
        fused_results
    ):

        reranked = []

        for doc, score in reranked_docs:

            for item in fused_results:

                if (
                    item["document"]
                    == doc
                ):

                    updated = item.copy()

                    updated[
                        "rerank_score"
                    ] = score

                    reranked.append(
                        updated
                    )

                    break

        return reranked

    def retrieve_context(
        self,
        query
    ):

        processed_query = (
            self.query_processor.process(
                query,
                self.state
            )
        )

        rewritten_query = (
            processed_query[
                "rewritten_query"
            ]
        )

        query_type = (
            processed_query[
                "query_type"
            ]
        )

        print(
            "Query:",
            rewritten_query
        )

        if query_type == "broad":

            self.state[
                "active_entity"
            ] = None

        where_filter = (
            category_filter(
                rewritten_query
            )
        )

        entity_filter = {}

        continuation_queries = [

            "where",

            "it",

            "that",

            "more",

            "explain",

            "used there",

            "used in it",

            "tell me more",

            "about it"
        ]

        should_attach_entity = any(

            word in rewritten_query.lower()

            for word in continuation_queries
        )

        if (
            query_type != "broad"
            and should_attach_entity
        ):

            entity_filter = (
                self.build_entity_filter()
            )

        if entity_filter:

            if where_filter:

                combined_filters = []

                for key, value in (
                    where_filter.items()
                ):

                    combined_filters.append({

                        key: value
                    })

                for key, value in (
                    entity_filter.items()
                ):

                    combined_filters.append({

                        key: value
                    })

                where_filter = {

                    "$and":
                    combined_filters
                }

            else:

                where_filter = (
                    entity_filter
                )

        print(
            "Where filter:",
            where_filter
        )

        dense_top_k = 6
        bm25_top_k = 6

        if query_type == "broad":

            dense_top_k = 20
            bm25_top_k = 20

        bm25_results = (
            self.bm25.retrieve(
                rewritten_query,
                where_filter=where_filter,
                top_k=bm25_top_k
            )
        )

        dense_results = (
            self.dense.retrieve(
                rewritten_query,
                where_filter=where_filter,
                top_k=dense_top_k
            )
        )
        if query_type != "broad":
            self.state = (

                self.query_processor
                .extract_entities(
                    dense_results,
                    self.state
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

        if query_type == "broad":

            reranked = (
                self.apply_entity_diversity(
                    fused_results
                )
            )

        else:

            reranked_docs = (
                self.reranker.rerank(
                    rewritten_query,
                    fused_documents
                )
            )

            reranked = (
                self.map_reranked_results(
                    reranked_docs,
                    fused_results
                )
            )

            reranked = (
                self.apply_entity_diversity(
                    reranked
                )
            )

        if query_type == "broad":

            final_docs = [

                item["document"]

                for item in reranked[:6]
            ]

        else:

            final_docs = [

                item["document"]

                for item in reranked[:4]
            ]

        print(
            "Final documents:",
            final_docs
        )

        if query_type == "broad":

            structured_context = []

            for index, doc in enumerate(
                final_docs,
                start=1
            ):

                structured_context.append(

                    f"""
                        ITEM {index}
                        
                        DESCRIPTION:
                        {doc}
                        """
                )

            context = "\n".join(
                structured_context
            )

        else:

            context = "\n\n".join(
                final_docs
            )

        self.state[
            "last_query"
        ] = rewritten_query

        return (
            context,
            query_type
        )

    def ask(
        self,
        query
    ):

        context, query_type = (
            self.retrieve_context(
                query
            )
        )

        prompt = (
            prompt_builder(
                query,
                context,
                query_type
            )
        )

        response = (
            generator(prompt)
        )

        self.state[
            "chat_history"
        ].append({

            "query": query,

            "response": response
        })

        return response