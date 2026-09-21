from shared.domain.ragrecord import RAGRecord
from app.storage.base import RAGRepository

class ChromaRepository(RAGRepository):

    def __init__(self, client, collection_name: str):
        self.collection = client.get_or_create_collection(
            name=collection_name
        )

    def add(self, records: list[RAGRecord]):

        self.collection.add(
            ids=[r.id for r in records],
            embeddings=[r.embedding for r in records],
            documents=[r.text for r in records],
            metadatas=[
                {
                    "document_id": r.document_id,
                    "chunk_id": r.chunk_id,
                    "page": r.page,
                }
                for r in records
            ],
        )

    def search(self, embedding: list[float], limit: int = 5) -> list[dict]:
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=limit,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        items = []
        for doc, meta, distance, result_id in zip(documents, metadatas, distances, ids):
            items.append({
                "id": result_id,
                "document_id": meta.get("document_id") if meta else None,
                "chunk_id": meta.get("chunk_id") if meta else None,
                "page": meta.get("page") if meta else None,
                "text": doc,
                "score": float(distance),
            })

        return items