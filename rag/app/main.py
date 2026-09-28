from fastapi import FastAPI
import chromadb
from app.services.ingestion_service import IngestionService
from app.storage.chroma import ChromaRepository
from app.ingestion.parser import PDFParser
from app.ingestion.chunker import TextChunker
from app.ingestion.embedder import Embedder
from app.api.router import create_router
from app.config import config
from shared.logging.logger import configure_logging, RunIDMiddleware

logger = configure_logging(__name__)

client = chromadb.Client()
parser = PDFParser()
chunker = TextChunker(max_size=config.MAX_SIZE, overlap=config.OVERLAP)
embedder = Embedder()
repository = ChromaRepository(client=client, collection_name="documents")
ingestion_service = IngestionService(parser, chunker, embedder, repository)

app = FastAPI()
app.add_middleware(RunIDMiddleware)

app.include_router(
    create_router(ingestion_service)
)

logger.info("RAG service initialized")