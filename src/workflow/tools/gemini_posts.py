from typing import Type
from pydantic import BaseModel, Field
from .base import VectorSearchInput, VectorSearchTool


class GeminiSearchInput(VectorSearchInput):
    query: str = Field(
        description='A query to search for Gemini related documents and posts. Must be in English.'
    )


class GeminiSearchTool(VectorSearchTool):
    name: str = "gemini_search"
    description: str = (
        "A tool for searching Gemini related documents and posts."
    )
    args_schema: Type[BaseModel] = GeminiSearchInput
    
    def __init__(self, *args, **kwargs):
        collection_name = "gemini_posts"
        super().__init__(collection_name=collection_name, **kwargs)  