# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# UV 패키지 매니저 설치
RUN pip install uv

# 프로젝트 파일 복사
COPY pyproject.toml uv.lock README.md ./

# 의존성 설치
RUN uv sync --frozen

# 애플리케이션 소스 코드 복사
COPY src/ ./src/

# 환경 변수 설정
ENV PYTHONPATH=/app

# 포트 노출
EXPOSE 8000

# 작업 디렉토리를 src로 변경
WORKDIR /app/src

# 애플리케이션 실행
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 