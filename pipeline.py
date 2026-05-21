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
        self.bm25 = BM25Retriever(self.documents)
        self.dense = DenseRetriever()
        self.reranker = Reranker()
        self.query_processor = QueryProcessor(self.documents)
        self.state = {
            "active_entity": None,
            "last_query": None,
            "last_broad_results": [],
            "last_query_type" : None,
            "chat_history": []
        }

    def build_entity_filter(self):
        where_filter = {}
        active_entity = self.state["active_entity"]

        #checking if past active entity is there
        if not active_entity:
            return where_filter

        entity_type = active_entity["type"]
        entity_value = active_entity["value"].lower()

        #multiple values - entities
        if entity_type == "project":
            where_filter["project"] = entity_value

        elif entity_type == "organization":
            where_filter["organization"] = entity_value

        elif entity_type == "skill":
            where_filter["skill"] = entity_value

        elif entity_type == "education":
            where_filter["institution"] = entity_value

        elif entity_type == "employment_type" and "experience" not in str(where_filter):
            where_filter["employment_type"] = entity_value


        return where_filter

    def apply_entity_diversity(self,results):
        unique_entities = set()
        filtered_results = []
        for item in results:
            metadata = item["metadata"]
            entity = ( metadata.get("project") or metadata.get("skill") or metadata.get("organization")
                    or metadata.get("institution") or item.get("id"))

            if not entity:
                entity = item["document"][:50]

            if entity not in unique_entities:

                unique_entities.add(entity)

                filtered_results.append(item)

        return filtered_results

    def map_reranked_results(self,reranked_docs,fused_results):
        reranked = []
        for doc, score in reranked_docs:
            for item in fused_results:
                if item["document"] == doc:
                    updated = item.copy()
                    updated["rerank_score"] = score
                    reranked.append(updated)
                    break
        return reranked

    def retrieve_context(self,query):

        processed_query = self.query_processor.process(query,self.state)
        rewritten_query = processed_query["rewritten_query"]

        query_type = processed_query["query_type"]

        where_filter = category_filter(rewritten_query)

        entity_filter = {}


        if self.state["active_entity"]:
            entity_filter = self.build_entity_filter()

        if entity_filter:
            if where_filter:
                combined_filters = []

                for key, value in where_filter.items():
                    combined_filters.append({key: value})

                for key, value in entity_filter.items():
                    combined_filters.append({key: value})

                where_filter = {"$and":combined_filters}
            else:

                where_filter = entity_filter

        dense_top_k = 6
        bm25_top_k = 6

        if query_type == "broad":
            dense_top_k = 20
            bm25_top_k = 20

        bm25_results = self.bm25.retrieve(rewritten_query,where_filter=where_filter,top_k=bm25_top_k)

        dense_results = self.dense.retrieve(rewritten_query,where_filter=where_filter, top_k=dense_top_k)

        if query_type != "broad":
            self.state = self.query_processor.extract_entities(dense_results,self.state)
            
        fused_results = reciprocal_rank_fusion(bm25_results,dense_results)
            
        fused_documents = [item["document"] for item in fused_results]

        if query_type == "broad":

            reranked = self.apply_entity_diversity(fused_results)
            final_docs = [item["document"] for item in reranked[:6]]
            structured_context = []

            for index, doc in enumerate(final_docs, start=1):
                structured_context.append(

                    f"{index}. {doc}"
                )
            self.state["last_broad_results"] = final_docs

            context = "\n".join(structured_context)
        else:
            reranked_docs = self.reranker.rerank(rewritten_query,fused_documents)

            reranked = self.map_reranked_results(reranked_docs,fused_results)
            
            reranked = self.apply_entity_diversity(reranked)

            final_docs = [item["document"] for item in reranked[:4]]
            context = "\n\n".join(final_docs)


        self.state["last_query"] = rewritten_query

        return (context,query_type)

    def ask(self, query):

        context, query_type = self.retrieve_context(query)

        if query_type == "broad":
            self.state["chat_history"].append({
                "query": query,
                "response": context
            })
            return context

        if not context.strip():
            return "I could not find that information."

        prompt = prompt_builder(query,context,query_type)

        response = generator(prompt)

        self.state["chat_history"].append({
            "query": query,
            "response": response
        })

        return response