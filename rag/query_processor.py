class QueryProcessor:

    def __init__(self,documents):

        self.organizations = set()

        self.projects = set()

        self.skills = set()

        self.skill_aliases = {
            "ai":"Artificial Intelligence",
            "ml":"Machine Learning",
            "machine learning": "Machine Learning",
            "artificial intelligence":"Artificial Intelligence",
            "rag": "Retrieval-Augmented Generation",
            "retrieval augmented generation": "Retrieval-Augmented Generation",
            "semantic search": "Semantic Search",
            "vector db": "ChromaDB",
            "vector database": "ChromaDB",
             "llm":"Phi-3",
            "llms":"Phi-3",
            "local llm":"Phi-3",
            "tensorflow":"TensorFlow",
            "flower":"Flower",
            "huggingface":"Hugging Face",
            "hugging face":"Hugging Face",
            "fastapi": "FastAPI",
            "flask":"Flask",
            "react":"React",
            "html":"HTML CSS JavaScript",
            "css":"HTML CSS JavaScript",
            "javascript":"HTML CSS JavaScript",
            "js":"HTML CSS JavaScript",
            "chromadb":"ChromaDB",
            "sentence transformers":"Sentence Transformers",
            "ollama":"Ollama",
            "phi3":"Phi-3",
            "phi-3": "Phi-3",
            "python":"Python",
            "btech" : "Bachelor of Technology",
        }

        self.organization_aliases = {

            "full time": "full_time",
            "full-time": "full_time",
            "job": "full_time",
            "internship": "internship",
            "intern": "internship",
            "narl": "internship"
        }

        self.education_aliases = {

            "btech":"bachelor of technology",
            "b.tech":"bachelor of technology",
            "inter":"intermediate education",
            "intermediate":"intermediate education",
            "12" : "intermediate education",
            "12th" : "intermediate education",
            "school":"secondary school education",
            "10":"secondary school education",
            "10th" : "secondary school education",
            "qualification": "education",
            "qualifications": "education",
            "degree": "education",
        }


        for doc in documents:

            metadata = doc["metadata"]
            if "organization"in metadata:
                self.organizations.add(metadata[ "organization"].lower())

            if "project"in metadata:
                self.projects.add(metadata["project"].lower())

            if "skill" in metadata:
                self.skills.add(metadata[ "skill"].lower())

    def detect_new_entity(self,query):

        query = query.lower()

        for project in self.projects:

            normalized_project = project.replace(" ", "")
            normalized_query = query.replace(" ", "")

            if project in query or normalized_project in normalized_query:
                return {
                    "type": "project",
                    "value": project
                }
        normalized_query = f" {query} "

        for alias, actual_edu in self.education_aliases.items():
            normalized_alias = f" {alias} "
            if normalized_alias in normalized_query:
                return {
                    "type": "education",
                    "value": actual_edu
                }

        for alias, actual_experience in self.organization_aliases.items():
            normalized_alias = f" {alias} "
            if normalized_alias in normalized_query:

                return {
                    "type":"employment_type",
                    "value":actual_experience
                }

        for org in self.organizations:
            if org in query:

                return {
                    "type":"employment_type",
                    "value":org
                }
        # aliases normalisaion

        for alias, actual_skill in self.skill_aliases.items():
            normalized_alias = f" {alias} "
            if normalized_alias in normalized_query:

                return {
                    "type": "skill",
                    "value": actual_skill
                }

        for skill in self.skills:
            if skill in query:
                return {
                    "type":"skill",
                    "value":skill
                }

        return None


    def is_new_topic(self, query):

        query = query.lower()
        broad_patterns = [
            "tell me about",
            "list",
            "show",
            "what are",
            "give",
            "all",
            "summary",
            "introduce"
        ]

        broad_categories = [
            "projects",
            "skills",
            "education",
            "experience",
            "achievements",
            "technologies",
            "qualification",
            "college",
            "profile"
        ]

        if any(
                pattern in query
                for pattern in broad_patterns
        ):

            if any(
                    category in query
                    for category in broad_categories
            ):
                return True

        return False

    def detect_query_type(self, query):

        query = query.lower()

        focused_patterns = [
            "where",
            "which",
            "used",
            "use",
            "using",
            "tell me more",
            "more about",
            "explain",
            "implemented",
            "worked on",
            "which project",
            "which skill",
            "which experience",
            "full time",
            "full-time",
            "internship",
            "intern"
        ]

        for pattern in focused_patterns:

            if pattern in query:
                return "focused"

        return "broad"

    def rewrite_query(self, query, state):

        query = query.lower()

        new_entity = self.detect_new_entity(query)

        if new_entity:
            state["active_entity"] = new_entity
            return query


        if self.is_new_topic(query):
            state["active_entity"] = None
            return query

        return query

    def extract_entities(self, dense_results, state):

        if not dense_results:
            return state

        if state.get("last_query_type") == "broad":
            return state

        metadata = dense_results[0]["metadata"]

        if "project" in metadata:
            state["active_entity"] = {
                "type":"project",
                "value":metadata["project"]
            }

        if "skill" in metadata:
            state["active_entity"] = {
                "type":"skill",
                "value": metadata["skill"]
            }

        if "organization" in metadata:
            state["active_entity"] = {
                "type":"organization",
                "value":metadata["organization"]
            }

        if "institution" in metadata:
            state["active_entity"] = {
                "type": "education",
                "value": metadata["institution"]
            }

        return state


    def process(self, query, state):

        rewritten_query = self.rewrite_query(query,state)

        query_type = self.detect_query_type(rewritten_query)
        state["last_query_type"] = query_type
        return {
            "query_type":query_type,
            "rewritten_query":rewritten_query
        }