from sentence_transformers import SentenceTransformer
from utils.config import EMBEDDING_MODEL

embedder = SentenceTransformer(
    EMBEDDING_MODEL
)

