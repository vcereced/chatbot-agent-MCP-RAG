from app.tools.base import BaseTool
from simpleeval import simple_eval

from shared.domain.tooldefinition import (
    ToolDefinition,
    ParameterDefinition,
    PropertyDefinition,
)


class CalculatorTool(BaseTool):

    def get_definition(self) -> ToolDefinition:

        return ToolDefinition(
            name="calculator",
            description="Evaluate a mathematical expression.",
            input_schema=ParameterDefinition(
                type="object",
                properties={
                    "expression": PropertyDefinition(
                        type="string",
                        description="Mathematical expression to evaluate.",
                    )
                },
                required=["expression"],
            ),
        )

    async def execute(self, arguments: dict[str, object]) -> object:
        expression = arguments.get("expression")
        if not expression or not isinstance(expression, str):
            raise ValueError("Parameter 'expression' must be a non-empty string.")

        # Se evalúa de forma 100% segura sin riesgo de inyección de código
        return simple_eval(expression)