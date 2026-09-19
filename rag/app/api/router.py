from fastapi import APIRouter, UploadFile, File
import uuid
from app.services.ingestion_service import IngestionService

from shared.logging.logger import configure_logging
logger = configure_logging(__name__)

def create_router(ingestion_service: IngestionService) -> APIRouter:

    router = APIRouter()

    @router.get("/health", status_code=200)
    async def health():
        return {"status": "ok"}
    
    @router.post("/ingest_documents")
    async def ingest_document(file: UploadFile = File(...)):
        logger.info("Rag service started to ingest file.")

        pdf_bytes = await file.read()

        document_id = str(uuid.uuid4())

        chunks_count = ingestion_service.ingest(
            pdf_bytes,
            document_id,
        )

        return {"chunks": chunks_count}

    @router.post("/search")
    async def search():
        pass

    return router