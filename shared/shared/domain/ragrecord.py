from pydantic import BaseModel


class RAGRecord(BaseModel):
    id: str # by IngestionService
    document_id: str #generado en router.py/ingest_document
    chunk_id: int # enumerate by services.py/IngestionService
    page: int
    text: str
    embedding: list[float]


class RAGSearchResult(BaseModel):
    record: RAGRecord
    score: float