from dotenv import load_dotenv
import asyncio
import os
from reader.pdf import PDFReader
from reader.html import HTMLReader
from chunker.token import TokenSizeChunker
from workflow.tools import *

load_dotenv(override=True)


path2tool = {
    "./data/gemini_v2_5_report.pdf": GeminiSearchTool,
    "./data/Claude_4_System_Card.pdf": AnthropicSearchTool,
    "https://model-spec.openai.com/2025-04-11.html": OpenaiSearchTool,
}
QDRANT_URL = os.getenv("QDRANT_URL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")


async def main():
    # Reader 초기화
    pdf_reader = PDFReader()
    html_reader = HTMLReader()
    
    # 청킹 설정
    chunker = TokenSizeChunker(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    for data_path, tool_class in path2tool.items():
        print(f"업로드 시작: {tool_class.__name__} - {data_path}")
        
        # 1. 파일 형태에 따라 적절한 reader 선택
        if data_path.endswith('.pdf'):
            text = pdf_reader(data_path)
            file_type = "pdf"
        elif data_path.endswith('.html') or data_path.startswith('http'):
            text = html_reader(data_path)
            file_type = "html"
        else:
            continue
            
        # 2. 텍스트 청킹
        documents = chunker(text, metadata={
            "file_path": data_path,
            "file_type": file_type
        })
        
        # 3. 해당 도구 초기화
        vector_tool = tool_class(
            qdrant_url=QDRANT_URL,
            embedding_model=EMBEDDING_MODEL
        )
        
        # 4. Qdrant에 문서 업로드 (컬렉션 생성)
        await vector_tool.upload_documents(
            documents=documents,
            vector_field="content",
            create_collection=True
        )


if __name__ == "__main__":
    asyncio.run(main()) 