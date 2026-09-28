from fastapi import APIRouter, UploadFile, File, HTTPException
from shared.domain.ragrecord import SearchRequest
import uuid
from app.services.ingestion_service import IngestionService
from time import perf_counter

from shared.logging.logger import configure_logging
logger = configure_logging(__name__)

def create_router(ingestion_service: IngestionService) -> APIRouter:

    router = APIRouter()

    @router.get("/health", status_code=200)
    async def health():
        return {"status": "ok"}

    @router.post("/ingest_documents")
    async def ingest_document(file: UploadFile = File(...)):
        started_at = perf_counter()
        logger.info("Document ingestion started")

        pdf_bytes = await file.read()

        document_id = str(uuid.uuid4())

        chunks_count = ingestion_service.ingest(
            pdf_bytes,
            document_id,
        )

        logger.info(
            "Document ingestion completed document_id=%s bytes=%d chunks=%d duration_ms=%.2f",
            document_id,
            len(pdf_bytes),
            chunks_count,
            (perf_counter() - started_at) * 1000,
        )

        return {"chunks": chunks_count}

    @router.post("/search")
    async def search(request: SearchRequest):
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="question is required.")

        started_at = perf_counter()
        logger.info(
            "RAG search started question_chars=%d limit=%d",
            len(request.question),
            request.limit,
        )

        results = ingestion_service.search(request.question, limit=request.limit)

        logger.info(
            "RAG search completed results=%d duration_ms=%.2f",
            len(results),
            (perf_counter() - started_at) * 1000,
        )

        return {"results": results}

    return router