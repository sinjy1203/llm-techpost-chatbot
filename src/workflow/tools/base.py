from typing import Type, Optional
import asyncio
from langchain_core.documents import Document
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from qdrant_client import AsyncQdrantClient, models
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm


class VectorSearchInput(BaseModel):
    query: str = Field(
        description='A query to search for similar documents.'
    )
    top_k: int = Field(
        description='The number of documents to return.',
        default=5
    )


class VectorSearchTool(BaseTool):
    name: str = "vector_search"
    description: str = (
        "A tool for searching documents similar to the query."
    )
    args_schema: Type[BaseModel] = VectorSearchInput
    return_direct: bool = False

    vectorstore: object
    embeddings: object
    vector_size: int
    collection_name: str

    def __init__(self, qdrant_url, collection_name, embedding_model):
        embeddings = OpenAIEmbeddings(model=embedding_model)
        vector_size = len(embeddings.embed_query("test"))
        super().__init__(
            vectorstore=AsyncQdrantClient(url=qdrant_url),
            embeddings=embeddings,
            vector_size=vector_size,
            collection_name=collection_name
        )

    async def upload_documents(self, documents: list[Document], vector_field: str = "content", create_collection: bool = False):
        if create_collection:
            await self.vectorstore.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )
        
        payloads = []
        vector_contents = []
        for doc in documents:
            vector_contents.append(doc[vector_field])
            payloads.append({k: v for k, v in doc.items()})

        vectors = self.batch_embed(vector_contents, batch_size=64)
        
        await self.vectorstore.upsert(
            collection_name=self.collection_name,
            points=models.Batch(
                ids=[i for i in range(len(documents))],
                vectors=vectors,
                payloads=payloads
            )
        )

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        return asyncio.run(self._arun(query, run_manager))

    async def _arun(
        self,
        query: str,
        top_k: int = 5,
        config: Optional[RunnableConfig] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ):
        
        vector = await self.embeddings.aembed_query(query)
        result = await self.vectorstore.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k
        )

        contexts = []
        for point in result.points:
            payload = point.payload
            contexts.append(
                {
                    "file_path": payload["file_path"],
                    "content": payload["content"],
                    "similarity_score": point.score
                }
            )
        return contexts
    
    def batch_embed(self, texts: list[str], batch_size: int):
        total_vectors = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        print(f"임베딩 생성 중... (총 {len(texts)}개 텍스트, {total_batches}개 배치)")
        
        for i in tqdm(range(0, len(texts), batch_size), 
                     desc="임베딩 처리", 
                     total=total_batches,
                     unit="batch"):
            batch = texts[i:i+batch_size]
            embeddings = self.embeddings.embed_documents(batch)
            total_vectors.extend(embeddings)
        
        print(f"임베딩 완료: {len(total_vectors)}개 벡터 생성")
        return total_vectors