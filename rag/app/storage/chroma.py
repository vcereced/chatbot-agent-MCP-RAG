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