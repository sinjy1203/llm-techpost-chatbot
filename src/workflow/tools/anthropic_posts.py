from typing import Type
from pydantic import BaseModel, Field
from .base import VectorSearchInput, VectorSearchTool


class AnthropicSearchInput(VectorSearchInput):
    query: str = Field(
        description='A query to search for Anthropic related documents and posts. Must be in English.'
    )


class AnthropicSearchTool(VectorSearchTool):
    name: str = "anthropic_search"
    description: str = (
        "A tool for searching Anthropic related documents and posts."
    )
    args_schema: Type[BaseModel] = AnthropicSearchInput
    
    def __init__(self, *args, **kwargs):
        collection_name = "anthropic_posts"
        super().__init__(collection_name=collection_name, **kwargs) 