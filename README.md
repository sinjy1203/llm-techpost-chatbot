# 기술블로그 RAG 기반 질의응답 Chatbot

Gemini, OpenAI, Anthropic 각각의 기술블로그 데이터(PDF, HTML)를 RAG(Retrieval-Augmented Generation)를 활용하여 사용자 질문에 답변하는 Agent 프로젝트입니다.

## 주요 기능
- **RESTful API**: HTTP API를 통한 Agent의 질의응답
- **Tracing**: Agent의 workflow 추적 기능 
- **Prompt Management**: Langfuse UI를 통한 prompt version 관리
- **Evaluation**: Agent의 문서 검색과 답변 생성에 대한 평가

## 기술 스택
- **Agent**: LangGraph, LangChain
- **Flow Tracing**: Lanfuse
- **Vector Database**: Qdrant
- **API Framework**: FastAPI
- **Language Model**: OpenAI GPT-4o-mini
- **Embedding Model**: Dense Embedding(text-embedding-3-small), Sparse Embedding(bm25)

### **Infrastructure & DevOps**
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Package Management**: UV (Python)
- **Environment Management**: python-dotenv

### **Data Processing**
- **PDF Processing**: PyMuPDF
- **HTML Processing**: BeautifulSoup4 + requests

### 데이터 소스
- **Gemini**: Gemini 2.5 Pro 기술 보고서 (PDF)
- **OpenAI**: Model Spec 문서 (HTML)  
- **Anthropic**: Claude 3 시스템 카드 (PDF)

## 프로젝트 구조

```
llm-techpost-chatbot/
│
├── 📁 src/                          # 메인 소스 코드
│   ├── 📁 reader/                   # 문서 리더 모듈
│   │   ├── pdf.py                   # PDF 파일 읽기
│   │   └── html.py                  # HTML/웹 페이지 읽기
│   │ 
│   ├── 📁 chunker/                  # 텍스트 청킹 모듈
│   │   └── token.py                 # 청크 사이즈 기반 청킹
│   │ 
│   ├── 📁 workflow/                 # Agent 워크플로우
│   │   ├── 📁 tools/                # 에이전트 도구들
│   │   │   ├── base.py              # Qdrant vector search base class
│   │   │   ├── gemini_posts.py      # Gemini 문서 검색
│   │   │   ├── openai_posts.py      # OpenAI 문서 검색
│   │   │   ├── anthropic_posts.py   # Anthropic 문서 검색
│   │   │   └── web.py               # 웹 검색 (Brave API)
│   │   ├── agent.py                 # ReactAgent 구현
│   │   ├── state.py                 # 상태 관리
│   │   └── prompt.py                # 시스템 프롬프트
│   │ 
│   ├── main.py                      # FastAPI 서버
│   ├── setup_prompt.py              # 초기 Agent system prompt를 langfuse에 업로드
│   ├── eval.py                      # Agent 평가 코드
│   └── upload_vectorstore.py        # 문서 벡터 스토어에 업로드
│
├── 📁 data/                         # 데이터 파일
│   ├── gemini_v2_5_report.pdf       # Gemini 기술 문서
│   ├── Claude_4_System_Card.pdf     # Anthropic 기술 문서
│   └── test_dataset.json            # Agent 평가 데이터셋
│
├── 📁 eval_result/                  # 평가 결과
│   └── 📁 %Y%m%d_%H%M%S/            # Gemini 기술 문서
│       ├── metric.py                # 평균 검색 정확도, 답변 정확도
│       └── test_dataset_eval.py    # 전체 검색 정확도, 답변 정확도
│
├── 📁 .github/workflows/            # GitHub Actions
│   └── docker-publish.yml          # Docker 이미지 자동 배포
│
├── docker-compose.yml              # 서비스 오케스트레이션
├── Dockerfile                      # 컨테이너 이미지 정의
├── .dockerignore                   # Docker 빌드 제외 파일
├── pyproject.toml                  # Python 의존성 관리
├── uv.lock                         # Python 의존성 고정
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

#### **데이터 인덱싱**
```bash
docker compose --profile init up -d
```

#### **API server 실행**
```bash
docker compose --profile api up -d
```

#### **Agent 평가**
```bash
docker compose --profile eval up -d
```

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
  "answer":"OpenAI에서 말하는 \"Assistant\"는 사용자가 상호작용하는 인공지능 엔티티를 의미합니다. 이 Assistant는 주로 대화 형식으로 구성된 메시지 목록을 기반으로 작동하며, 사용자의 질문이나 요청에 대해 응답하는 역할을 합니다. OpenAI의 모델은 이러한 대화 형식에 맞춰 훈련되어 있으며, 사용자가 입력한 메시지에 대해 적절한 응답을 생성하는 데 최적화되어 있습니다.\n\n### Assistant의 주요 특징\n1. **대화형 인터페이스**: Assistant는 사용자가 입력한 메시지에 대해 대화 형식으로 응답합니다. 이 대화는 사용자의 메시지, Assistant의 응답, 그리고 경우에 따라 도구와의 상호작용을 포함합니다.\n   \n2. **사용자와의 상호작용**: Assistant는 최종 사용자 또는 개발자가 상호작용하는 주체로, 사용자의 질문에 대한 답변을 제공하거나 요청을 처리합니다. 사용자는 Assistant의 응답을 통해 정보를 얻거나 문제를 해결할 수 있습니다.\n\n3. **모델의 역할**: Assistant는 OpenAI의 언어 모델을 기반으로 하며, 이 모델은 대화의 한 참가자로서만 작동합니다. 즉, Assistant는 사용자의 요청에 대한 응답을 생성하는 데 집중하며, 다른 역할(예: 개발자나 시스템 메시지의 역할)은 수행하지 않습니다.\n\n4. **인간 중심의 가치**: Assistant는 OpenAI의 목표에 따라 인류의 복지와 진실을 중요시하며, 사용자의 질문에 대해 긍정적이고 친절한 태도로 응답하도록 설계되었습니다.\n\n이러한 특성 덕분에 OpenAI의 Assistant는 다양한 응용 프로그램에서 유용하게 사용될 수 있으며, 사용자와의 상호작용을 통해 지속적으로 발전하고 있습니다.\n\n자세한 내용은 [OpenAI 모델 사양 문서](https://model-spec.openai.com/2025-04-11.html)에서 확인할 수 있습니다."
}
```

## **Langfuse Prompt management 사용법**
- **URL**: http://localhost:3000
- Webhooks 설정
  1. 왼쪽 사이드 탭에서 `Prompts` 클릭 후에 오른쪽 상단에 `Webhooks` 클릭
  2. `Create Webhook` 클릭 후 `Webhook URL`에 "http://api:8000/prompt/reload" 작성 후 `Save Webhook` 클릭
- `Prompts`에서 
"react-agent-system-prompt"에서 프롬프트 생성후 `production` version label을 해주면 Webhook을 통해 자동으로 api 서버에 적용됨


## LLM-as-a-Judge를 통한 Agent 평가
- 평가 코드: `./src/eval.py`
- 평가 데이터셋: `./data/test_dataset.json` (한 문서부터 복수 문서가 필요한 질문들로 구성)
- metric
  - "retrieved_context_score": 검색 결과와 정답 references를 비교하여 핵심 내용이 포함됐는지 판단
  - "generated_answer_score": 정답 answer에서 핵심 요소를 파악하고 해당 요소들이 생성된 답변에 포함됐는지 판단
### 평가 결과
| Search Type      | retrieved_context_score_mean | generated_answer_score_mean |
|------------------|-----------------------------|----------------------------|
| Semantic Search  | 0.38571428571428573            | 0.6428571428571429           |
| Hybrid Search    | 0.5285714285714286          | 0.7571428571428571        |


## Workflow 설계
**싱글 React Agent 아키텍처**를 기반으로 하며, 각 기술 블로그(문서)별로 분리된 벡터 데이터베이스 컬렉션과 웹 검색 툴을 동적으로 활용하는 구조로 설계되었습니다.

### 주요 구조
- **Agent (src/workflow/agent.py)**  
  - LangGraph 기반의 React Agent로, 사용자 질문을 받아 적절한 툴(tool)을 선택하고, 툴의 결과를 바탕으로 최종 답변을 생성
- **State 관리 (src/workflow/state.py)**  
  - State: Agent workflow 각 노드의 결과 저장을 위한 스키마 (messages, execute_tool_count)
  - Config: tool 선택 최대 수 관리를 위한 Agent workflow 설정 스키마 (max_execute_tool_count)
- **프롬프트 관리 (src/workflow/prompt.py)**  
  - React Agent system prompt: 툴 선택 또는 답변 생성을 위한 프롬프트 (문서 출처 표기)
- **Tool 모듈 (src/workflow/tools/)**
  - **base.py**: Qdrant 기반 hybrid search tool의 공통 로직을 정의
  - **gemini_posts.py, openai_posts.py, anthropic_posts.py**: 각 문서(Gemini, OpenAI, Anthropic)별로 분리된 벡터 DB 컬렉션에 대한 검색 툴
  - **web.py**: Brave API를 활용한 웹 검색 툴

### 동작 방식
1. **질문 분석 및 Tool 선택**
    - `llm` Node
    - 에이전트는 사용자의 질문을 분석하여, 필요한 툴을 선택하고 그에 맞는 query를 생성
2. **Tool 실행**  
    - `execute_tool` Node
    - llm이 선택한 노드와 query를 통해 vector search 수행
3. **검색 결과 기반 답변 생성**  
    - `llm` Node
    - 선택된 툴의 검색 결과를 바탕으로 llm이 추가 툴을 선택하거나 최종 답변을 생성

### 설계 이유 및 장점
- **문서별 컬렉션 분리**  
  - 각 기술 블로그의 성격이 명확히 구분되므로, 질문이 특정 문서에 대한 것인지 쉽게 파악 가능
  - 예를 들어, "OpenAI에서 말하는 Assistant는 어떤 것을 의미하나요?"와 같은 질문은 OpenAI 문서 컬렉션에서만 검색하면 되므로, 전체 문서를 대상으로 검색하는 것보다 검색 정확도 향상 예상됨
- **동적 툴 (Collection) 선택**  
  - 사용자의 질문 의도에 따라 적절한 컬렉션을 동적으로 선택할 수 있어 "AI 모델의 멀티모달 기능을 비교해주세요"와 같이 여러 문서를 아우르는 질문도 유연하게 처리 가능
- **React Agent 구조**  
  - 툴 결과에 따라 반복적으로 선택할 수 있게 하여 복잡한 질문도 처리 가능
- **확장성**  
  - 새로운 문서나 데이터 소스가 추가될 경우, 별도의 툴과 컬렉션만 추가하면 되므로 유지보수와 확장에 용이

## 개발 의도 및 개선 전략
제한된 일주일이라는 기간 동안 많은 성능 개선을 이루기는 어렵다고 판단하여, 성능 개선이 가능한 기반을 마련하는 데 중점을 두었습니다.

- **Agent Workflow 추적**: Agent workflow의 각 노드 결과를 Langfuse UI를 통해 시각적으로 추적할 수 있도록 하여, 디버깅과 문제 원인 분석이 용이하도록 설계하였습니다.
- **프롬프트 버전 관리**: React Agent의 시스템 프롬프트를 Langfuse UI에서 버전 관리할 수 있게 하여, 프롬프트 개선 및 답변 정확도 향상에 유리한 구조를 마련하였습니다.
- **평가 및 개선 사이클**: 개발한 Workflow의 성능을 LLM-as-a-Judge 기반 평가 코드로 측정할 수 있도록 하여, 실제 개선이 이루어졌는지 객관적으로 파악할 수 있게 하였습니다.

이러한 구조를 통해, 단기간 내에 완성도를 높이기보다는 장기적으로 성능 개선과 유지보수가 용이한 RAG 기반 질의응답 시스템을 구축하는 데 집중하였습니다.
