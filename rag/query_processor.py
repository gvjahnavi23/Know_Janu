from utils.helper import (
    follow_up
)


class QueryProcessor:

    def __init__(
        self,
        documents
    ):

        self.follow_up_words = (
            follow_up()
        )

        self.organizations = set()

        self.projects = set()

        self.skills = set()

        # --------------------------------
        # Skill aliases / normalization
        # --------------------------------

        self.skill_aliases = {

            # --------------------------------
            # AI / ML
            # --------------------------------

            "ai":
            "Artificial Intelligence",

            "ml":
            "Machine Learning",

            "machine learning":
            "Machine Learning",

            "artificial intelligence":
            "Artificial Intelligence",

            # --------------------------------
            # RAG / Search
            # --------------------------------

            "rag":
            "Retrieval-Augmented Generation",

            "retrieval augmented generation":
            "Retrieval-Augmented Generation",

            "semantic search":
            "Semantic Search",

            "vector db":
            "ChromaDB",

            "vector database":
            "ChromaDB",

            # --------------------------------
            # LLM
            # --------------------------------

            "llm":
            "Phi-3",

            "llms":
            "Phi-3",

            "local llm":
            "Phi-3",

            # --------------------------------
            # Frameworks
            # --------------------------------

            "tensorflow":
            "TensorFlow",

            "flower":
            "Flower",

            "huggingface":
            "Hugging Face",

            "hugging face":
            "Hugging Face",

            # --------------------------------
            # Backend
            # --------------------------------

            "fastapi":
            "FastAPI",

            "flask":
            "Flask",

            # --------------------------------
            # Frontend
            # --------------------------------

            "react":
            "React",

            "html":
            "HTML CSS JavaScript",

            "css":
            "HTML CSS JavaScript",

            "javascript":
            "HTML CSS JavaScript",

            "js":
            "HTML CSS JavaScript",

            # --------------------------------
            # Database
            # --------------------------------

            "chromadb":
            "ChromaDB",

            # --------------------------------
            # Embeddings
            # --------------------------------

            "sentence transformers":
            "Sentence Transformers",

            # --------------------------------
            # Local inference
            # --------------------------------

            "ollama":
            "Ollama",

            "phi3":
            "Phi-3",

            "phi-3":
            "Phi-3",

            # --------------------------------
            # Programming
            # --------------------------------

            "python":
            "Python"
        }

        for doc in documents:

            metadata = (
                doc["metadata"]
            )

            if (
                "organization"
                in metadata
            ):

                self.organizations.add(

                    metadata[
                        "organization"
                    ].lower()
                )

            if (
                "project"
                in metadata
            ):

                self.projects.add(

                    metadata[
                        "project"
                    ].lower()
                )

            if (
                "skill"
                in metadata
            ):

                self.skills.add(

                    metadata[
                        "skill"
                    ].lower()
                )

    # --------------------------------
    # Detect explicit entities
    # --------------------------------

    def detect_new_entity(
        self,
        query
    ):

        query = query.lower()

        # aliases first

        for alias, actual_skill in (

            self.skill_aliases.items()

        ):

            if alias in query:

                return {

                    "type":
                    "skill",

                    "value":
                    actual_skill
                }

        for org in self.organizations:

            if org in query:

                return {

                    "type":
                    "organization",

                    "value":
                    org
                }

        for project in self.projects:

            if project in query:

                return {

                    "type":
                    "project",

                    "value":
                    project
                }

        for skill in self.skills:

            if skill in query:

                return {

                    "type":
                    "skill",

                    "value":
                    skill
                }

        return None

    # --------------------------------
    # Check if query already
    # contains a new entity
    # --------------------------------

    def contains_new_entity(
        self,
        query
    ):

        query = query.lower()

        for alias in (
            self.skill_aliases
        ):

            if alias in query:

                return True

        for org in self.organizations:

            if org in query:

                return True

        for project in self.projects:

            if project in query:

                return True

        for skill in self.skills:

            if skill in query:

                return True

        return False

    # --------------------------------
    # Follow-up detection
    # --------------------------------

    def is_follow_up(
        self,
        query
    ):

        query = query.lower()

        for word in (
            self.follow_up_words
        ):

            if word in query:

                return True

        return False

    # --------------------------------
    # Broad topic detection
    # --------------------------------

    def is_new_topic(
        self,
        query
    ):

        query = query.lower()

        keywords = [

            "projects",
            "skills",
            "education",
            "experience",
            "achievements",
            "technologies",
            "qualification",
            "btech",
            "college",
            "summary",
            "about me",
            "about jahnavi",
            "profile",
            "who is jahnavi",
            "introduce"
        ]

        for keyword in keywords:

            if keyword in query:

                return True

        return False

    # --------------------------------
    # Query type classification
    # --------------------------------

    def detect_query_type(
        self,
        query
    ):

        if (
            self.is_new_topic(query)
        ):

            return "broad"

        return "focused"

    # --------------------------------
    # Conversational query rewriting
    # --------------------------------

    def rewrite_query(
        self,
        query,
        state
    ):

        new_entity = (
            self.detect_new_entity(
                query
            )
        )

        # ----------------------------
        # NEW ENTITY
        # ----------------------------

        if new_entity:

            state[
                "active_entity"
            ] = new_entity

            return query

        # ----------------------------
        # NEW TOPIC
        # ----------------------------

        if (
            self.is_new_topic(query)
        ):

            state[
                "active_entity"
            ] = None

            return query

        # ----------------------------
        # FOLLOW-UP
        # ----------------------------

        if (

            self.is_follow_up(query)

            and state[
                "active_entity"
            ]

            and not self.contains_new_entity(
                query
            )
        ):

            entity = (

                state[
                    "active_entity"
                ]["value"]
            )

            return (
                f"{query} about "
                f"{entity}"
            )

        return query

    # --------------------------------
    # Extract entities from retrieval
    # --------------------------------

    def extract_entities(
        self,
        dense_results,
        state
    ):

        if not dense_results:

            return state

        metadata = (
            dense_results[0]["metadata"]
        )

        if "project" in metadata:

            state[
                "last_project"
            ] = metadata["project"]

            state[
                "active_entity"
            ] = {

                "type":
                "project",

                "value":
                metadata["project"]
            }

        if "skill" in metadata:

            state[
                "last_skill"
            ] = metadata["skill"]

            state[
                "active_entity"
            ] = {

                "type":
                "skill",

                "value":
                metadata["skill"]
            }

        if "organization" in metadata:

            state[
                "last_organization"
            ] = metadata[
                "organization"
            ]

            state[
                "active_entity"
            ] = {

                "type":
                "organization",

                "value":
                metadata[
                    "organization"
                ]
            }

        return state

    # --------------------------------
    # Main processing
    # --------------------------------

    def process(
        self,
        query,
        state
    ):

        rewritten_query = (
            self.rewrite_query(
                query,
                state
            )
        )

        query_type = (
            self.detect_query_type(
                rewritten_query
            )
        )

        return {

            "query_type":
            query_type,

            "rewritten_query":
            rewritten_query
        }