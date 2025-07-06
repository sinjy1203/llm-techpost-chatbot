import os
import json
import requests
import httpx
import asyncio
from dotenv import load_dotenv
from typing import Type, Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


URL = "https://api.search.brave.com/res/v1/web/search"


class WebSearchInput(BaseModel):
    query: str = Field(
        description="A query to search the web. Must be in English."
    )
    top_k: int = Field(
        description="The number of results to return",
        default=5
    )

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "A tool for searching the web"
    args_schema: Type[BaseModel] = WebSearchInput
    return_direct: bool = False

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None):
        return asyncio.run(self._arun(query, run_manager))

    async def _arun(
        self,
        query: str,
        top_k: int = 5,
        config: Optional[RunnableConfig] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ):
        async with httpx.AsyncClient() as client:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": os.getenv("BRAVE_API_KEY")
            }
            params = {
                "q": query,
                "count": top_k
            }
            response = await client.get(URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        results = data['web']['results'][:top_k]
        results = [
            {"title": item['title'], "time": item.get('page_age', ''), "content": item['description']}
            for item in results
        ]

        return results
