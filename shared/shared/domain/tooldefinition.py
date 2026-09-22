from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


JsonType = Literal[
    "string",
    "integer",
    "number",
    "boolean",
    "array",
    "object",
    "null",
]


class PropertyDefinition(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )

    type: JsonType | list[JsonType] | None = None
    description: str | None = None
    title: str | None = None
    default: Any = None
    enum: list[Any] | None = None

    any_of: list[PropertyDefinition] | None = Field(
        default=None,
        alias="anyOf",
    )
    one_of: list[PropertyDefinition] | None = Field(
        default=None,
        alias="oneOf",
    )
    all_of: list[PropertyDefinition] | None = Field(
        default=None,
        alias="allOf",
    )
    items: PropertyDefinition | None = None
    properties: dict[str, PropertyDefinition] | None = None
    required: list[str] | None = None

    ref: str | None = Field(default=None, alias="$ref")
    defs: dict[str, PropertyDefinition] | None = Field(
        default=None,
        alias="$defs",
    )


class ParameterDefinition(PropertyDefinition):
    type: Literal["object"] = "object"
    properties: dict[str, PropertyDefinition] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_required(self) -> "ParameterDefinition":
        for field in self.required:
            if field not in self.properties:
                raise ValueError(
                    f"'{field}' está en 'required' pero no está definido "
                    "en 'properties'."
                )
        return self


class ToolDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    description: str
    input_schema: ParameterDefinition
    output_schema: PropertyDefinition | None = None