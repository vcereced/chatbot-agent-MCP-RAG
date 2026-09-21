import httpx

from app.tools.base import BaseTool
from shared.domain.tooldefinition import (
    ToolDefinition,
    ParameterDefinition,
    PropertyDefinition,
)


class RAGSearchTool(BaseTool):

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="rag_search",
            description="Busca información relevante en los documentos indexados por el sistema RAG para responder una pregunta.",
            input_schema=ParameterDefinition(
                type="object",
                properties={
                    "question": PropertyDefinition(
                        type="string",
                        description="Pregunta o consulta sobre los documentos indexados.",
                    ),
                    "limit": PropertyDefinition(
                        type="string",
                        description="Número máximo de fragmentos a recuperar. Ejemplo: 5.",
                    ),
                },
                required=["question"],
            ),
        )

    async def execute(self, arguments: dict[str, object]) -> object:
        query = arguments.get("question")
        if not "question" or not isinstance("question", str):
            raise ValueError("Parameter 'question' must be a non-empty string.")

        limit = arguments.get("limit", 2)
        if isinstance(limit, str):
            try:
                limit = int(limit)
            except ValueError as exc:
                raise ValueError("Parameter 'limit' must be an integer.") from exc

        response = httpx.post(
            "http://rag:8000/search",
            json={"question": "question", "limit": limit},
            timeout=30,
        )
        response.raise_for_status()

        payload = response.json()
        return payload.get("results", [])
