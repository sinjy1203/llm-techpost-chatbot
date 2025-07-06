# 기술블로그 RAG 기반 질의응답 Chatbot

Gemini, OpenAI, Anthropic 각각의 기술블로그 데이터(PDF, HTML)를 RAG(Retrieval-Augmented Generation)를 활용하여 사용자 질문에 답변하는 Agent 프로젝트입니다.

## 주요 기능

- **문서 기반 답변**: 수집된 기술블로그 데이터를 기반으로 사용자 질문에 답변
- **웹서치 보완**: 주어진 문서로 답변이 불가능한 질문은 웹서치 툴을 활용
- **한국어 지원**: 모든 질문과 답변은 한국어로 처리
- **RESTful API**: HTTP API를 통한 질의응답 서비스 제공

## 기술 스택

- **Agent**: LangGraph, LangChain
- **Vector Database**: Qdrant
- **API Framework**: FastAPI
- **배포**: Docker

## 설치 및 실행

### Docker를 사용한 실행

1. 환경 변수 설정:
```bash
cp .env.example .env
# .env 파일에서 OPENAI_API_KEY, BRAVE_API_KEY 설정 필요
```

2. 서비스 실행:
```bash
docker-compose up -d
```

3. API 접근:
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs

## API 사용법

### 질문하기

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI 모델의 멀티모달 기능을 비교해주세요"}'
```

### 응답 예시

```json
{
  "answer": "멀티모달 AI 모델 비교 분석 결과..."
}
```

## 데이터 소스

- Gemini 기술블로그 (PDF)
- OpenAI 기술블로그 (HTML)
- Anthropic 기술블로그 (PDF)
