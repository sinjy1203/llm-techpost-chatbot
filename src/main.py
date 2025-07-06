import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

from workflow import ReactAgent
from workflow.tools import *
from workflow.state import State

# 환경 변수 로드
load_dotenv(override=True)

LLM_MODEL = os.getenv("LLM_MODEL")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
QDRANT_URL = os.getenv("QDRANT_URL")
MAX_EXECUTE_TOOL_COUNT = int(os.getenv("MAX_EXECUTE_TOOL_COUNT"))


# 전역 변수로 agent 저장
agent_graph = None


class ChatRequest(BaseModel):
    query: str = Field(
        ..., 
        description="유저의 질문", 
        min_length=1,
        example="AI 모델의 멀티모달 기능을 비교해주세요"
    )


class ChatResponse(BaseModel):
    answer: str = Field(..., description="질문에 대한 응답")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan 이벤트 핸들러"""
    global agent_graph
    
    print("🤖 Agent 초기화 중...")

    agent_graph = ReactAgent(
        model_kwargs={
            "model": LLM_MODEL,
            "temperature": LLM_TEMPERATURE
        },
        tools=[
            GeminiSearchTool(
                qdrant_url=QDRANT_URL,
                embedding_model=EMBEDDING_MODEL
            ),
            OpenaiSearchTool(
                qdrant_url=QDRANT_URL,
                embedding_model=EMBEDDING_MODEL
            ),
            AnthropicSearchTool(
                qdrant_url=QDRANT_URL,
                embedding_model=EMBEDDING_MODEL
            )
        ]
    )
    
    print("✅ Agent 초기화 완료!")
    
    yield
    
    # 종료 시 정리 작업
    print("🔄 Agent 종료 중...")
    agent_graph = None


# FastAPI 앱 생성
app = FastAPI(
    title="기술블로그 RAG 기반 질의응답 API",
    description="Gemini, OpenAI, Anthropic 기술블로그 데이터를 기반으로 질문에 답변하는 AI 어시스턴트",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """API 상태 확인"""
    return {"message": "기술블로그 RAG 기반 질의응답 API가 실행 중입니다."}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """사용자 질문에 대한 답변 생성"""
    global agent_graph
    
    if agent_graph is None:
        raise HTTPException(status_code=500, detail="Agent가 초기화되지 않았습니다.")
    
    try:
        # 초기 상태 설정
        initial_state = State(
            messages=[HumanMessage(content=request.query)],
            execute_tool_count=0
        )
        
        # 설정값
        config = {
            "configurable": {
                "max_execute_tool_count": MAX_EXECUTE_TOOL_COUNT
            }
        }
        
        # Agent 실행
        result = await agent_graph.ainvoke(initial_state, config)
        
        # 마지막 AI 메시지 추출
        final_answer = result["messages"][-1].content
        
        if not final_answer:
            raise HTTPException(status_code=500, detail="답변을 생성할 수 없습니다.")
        
        return ChatResponse(answer=final_answer)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"답변 생성 중 오류가 발생했습니다: {str(e)}")


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "agent_initialized": agent_graph is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 