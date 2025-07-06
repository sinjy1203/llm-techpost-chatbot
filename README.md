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
- **Language Model**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small

### **Infrastructure & DevOps**
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Package Management**: UV (Python)
- **Environment Management**: python-dotenv

### **Data Processing**
- **PDF Processing**: PyMuPDF
- **HTML Processing**: BeautifulSoup4 + requests

## 📁 프로젝트 구조

```
llm-techpost-chatbot/
├── 📁 src/                          # 메인 소스 코드
│   ├── 📁 reader/                   # 문서 리더 모듈
│   │   ├── pdf.py                   # PDF 파일 읽기
│   │   └── html.py                  # HTML/웹 페이지 읽기
│   ├── 📁 chunker/                  # 텍스트 청킹 모듈
│   │   └── token.py                 # 청크 사이즈 기반 청킹
│   ├── 📁 workflow/                 # Agent 워크플로우
│   │   ├── 📁 tools/                # 에이전트 도구들
│   │   │   ├── base.py              # 기본 벡터 검색 도구
│   │   │   ├── gemini_posts.py      # Gemini 문서 검색
│   │   │   ├── openai_posts.py      # OpenAI 문서 검색
│   │   │   ├── anthropic_posts.py   # Anthropic 문서 검색
│   │   │   └── web.py               # 웹 검색 (Brave API)
│   │   ├── agent.py                 # ReactAgent 구현
│   │   ├── state.py                 # 상태 관리
│   │   └── prompt.py                # 시스템 프롬프트
│   ├── main.py                      # FastAPI 서버
│   └──  upload_vectorstore.py       # 벡터 데이터 업로드
├── 📁 data/                         # 데이터 파일
│   ├── gemini_v2_5_report.pdf       # Gemini 기술 문서
│   └── Claude_4_System_Card.pdf     # Anthropic 기술 문서
├── 📁 .github/workflows/            # GitHub Actions
│   └── docker-publish.yml          # Docker 이미지 자동 배포
├── docker-compose.yml              # 서비스 오케스트레이션
├── Dockerfile                      # 컨테이너 이미지 정의
├── .dockerignore                   # Docker 빌드 제외 파일
├── pyproject.toml                  # Python 의존성 관리
└── README.md                       # 프로젝트 문서
```

## 빠른 시작

### **1. 저장소 클론**
```bash
git clone https://github.com/sinjy1203/llm-techpost-chatbot.git
cd llm-techpost-chatbot
```

### **2. 환경 변수 설정**
```bash
cp .env.example .env
# .env 파일에서 OPENAI_API_KEY, BRAVE_API_KEY 설정 필요
```

### **3. 서비스 실행**

#### **첫 번째 실행 (데이터 업로드 + API 서버)**
```bash
# 초기 데이터 업로드와 함께 실행
docker-compose --profile init up -d
```

#### **일반 실행 (API만)**
```bash
# 이미 데이터가 있는 경우
docker-compose up -d
```

### **4. API 접근**
- **API 서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## API 사용법

### **채팅 엔드포인트**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "OpenAI에서 말하는 Assistant는 어떤 것을 의미하나요?"
  }'
```

### **응답 예시**
```json
{
  "answer": "기술 블로그 문서에 따르면 ..."
}
```

## 데이터 소스

- **Gemini**: Gemini 2.5 Pro 기술 보고서 (PDF)
- **OpenAI**: Model Spec 문서 (HTML)  
- **Anthropic**: Claude 3 시스템 카드 (PDF)

## Docker Compose 서비스 구성

- **qdrant**: 벡터 데이터베이스 (포트: 6333)
- **upload**: 데이터 업로드 (일회성 실행)
- **api**: FastAPI 서버 (포트: 8000)


## CI/CD 파이프라인

### **자동 배포**
- **트리거**: `main` 브랜치에 push
- **동작**: Docker 이미지 빌드 → Docker Hub 업로드
- **플랫폼**: linux/amd64, linux/arm64 (M1/M2 Mac 지원)
