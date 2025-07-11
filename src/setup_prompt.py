import os
import logging
from dotenv import load_dotenv
from langfuse import get_client
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError
from workflow.prompt import SYSTEM_TEMPLATE


# 환경 변수 로드
load_dotenv(override=True)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_system_prompt(langfuse_client):
    """시스템 프롬프트를 Langfuse에 업로드"""
    
    # Langfuse 클라이언트 초기화

    try:
        # 프롬프트 존재 여부 확인
        existing_prompt = langfuse_client.get_prompt("react-agent-system-prompt")
        logger.info(f"✅ 프롬프트가 이미 존재합니다: {existing_prompt.name} (버전: {existing_prompt.version})")
        return
    except NotFoundError:
        # 프롬프트가 존재하지 않는 경우 생성
        logger.info("📝 프롬프트가 존재하지 않아 새로 생성합니다...")
    except Exception as e:
        logger.error(f"❌ 프롬프트 확인 중 다른 오류 발생: {str(e)}")
        return
    
    try:
        # 프롬프트 생성
        prompt = langfuse_client.create_prompt(
            name="react-agent-system-prompt",
            prompt=SYSTEM_TEMPLATE,
            labels=["production"]
        )
        logger.info(f"✅ 프롬프트가 성공적으로 생성되었습니다: {prompt.name} (버전: {prompt.version})")
    except Exception as e:
        logger.error(f"❌ 프롬프트 업로드 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    langfuse_client = get_client()
    setup_system_prompt(langfuse_client) 