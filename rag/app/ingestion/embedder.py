from sentence_transformers import SentenceTransformer


class Embedder:

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> [float]:
        embeddings = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embeddings