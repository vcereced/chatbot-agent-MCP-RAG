from app.ingestion.parser import PDFParser
from app.ingestion.chunker import TextChunker
from app.ingestion.embedder import Embedder
from shared.domain.ragrecord import RAGRecord
from app.storage.chroma import RAGRepository

from shared.logging.logger import configure_logging
logger = configure_logging(__name__)

class IngestionService:

    def __init__(self, parser: PDFParser, chunker: TextChunker, embedder: Embedder, repository: RAGRepository):
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder
        self.repository = repository

    def ingest(self, pdf_bytes: bytes, document_id: str):

        pages = self.parser.parse(pdf_bytes) #-> list[page, text]

        chunks = self.chunker.chunk(pages)#->list[page, text (chunked)]

        records = [] #list[RagRecord]

        for chunk_id, chunk in enumerate(chunks):

            embedding = self.embedder.embed(chunk["text"]) # -> [float]

            records.append(
                RAGRecord(
                    id=f"{document_id}_{chunk_id}",#no se repite
                    document_id=document_id,
                    chunk_id=chunk_id,
                    page=chunk["page"],
                    text=chunk["text"],
                    embedding=embedding.tolist(),
                )
            )

        logger.info(records)
        self.repository.add(records)
        logger.info(f"Created ={len(records)} records of the document.")
        return len(records)