from abc import ABC, abstractmethod
from shared.domain.ragrecord import RAGRecord

class RAGRepository(ABC):

    @abstractmethod
    def add(self, records: list[RAGRecord]) -> None:
        pass

    @abstractmethod
    def search(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[dict]:
        pass