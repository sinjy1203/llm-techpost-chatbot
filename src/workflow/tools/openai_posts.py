from typing import Type
from pydantic import BaseModel, Field
from .base import VectorSearchInput, VectorSearchTool


class OpenaiSearchInput(VectorSearchInput):
    query: str = Field(
        description='A query to search for OpenAI related documents and posts. Must be in English.'
    )


class OpenaiSearchTool(VectorSearchTool):
    name: str = "openai_search"
    description: str = (
        "A tool for searching OpenAI related documents and posts."
    )
    args_schema: Type[BaseModel] = OpenaiSearchInput
    
    def __init__(self, *args, **kwargs):
        collection_name = "openai_posts"
        super().__init__(collection_name=collection_name, **kwargs) 