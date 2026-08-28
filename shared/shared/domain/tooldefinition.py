from typing import Literal
from pydantic import BaseModel, Field, model_validator


class PropertyDefinition(BaseModel):
    type: Literal[
        "string",
        "integer",
        "number",
        "boolean",
        "array",
        "object",
    ]
    description: str | None = None


class ParameterDefinition(BaseModel):
    type: Literal["object"] = "object"  # Se puede poner "object" por defecto
    properties: dict[str, PropertyDefinition] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)  # Evita obligar a pasar []

    @model_validator(mode="after")
    def validate_required(self) -> "ParameterDefinition":
        # Comprobación segura
        for field in self.required:
            if field not in self.properties:
                raise ValueError(
                    f"'{field}' está en 'required' pero no está definido en 'properties'."
                )
        return self


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: ParameterDefinition