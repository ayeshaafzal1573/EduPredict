from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from typing import Any

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, 
        _core_schema: Any, 
        handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # This tells Pydantic v2 how to represent it in OpenAPI/JSON Schema
        return {"type": "string", "example": "60d5ec49f2954b2d88c9d7d2"}
