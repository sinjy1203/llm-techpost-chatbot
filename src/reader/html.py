import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class HTMLReader:
    """HTML URL을 읽고 텍스트를 추출하는 클래스"""
    
    def __init__(self):
        """HTMLReader 초기화"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def __call__(self, url: str) -> str:
        """
        HTML URL을 읽고 텍스트를 추출합니다.
        
        Args:
            url (str): HTML URL
            
        Returns:
            str: 추출된 텍스트
            
        Raises:
            ValueError: 유효하지 않은 URL일 경우
            requests.RequestException: HTTP 요청 실패 시
            Exception: 기타 오류 발생 시
        """
        try:
            # URL 유효성 검사
            if not self._is_valid_url(url):
                raise ValueError(f"유효하지 않은 URL입니다: {url}")
            
            # HTML 내용 가져오기
            html_content = self._fetch_html(url)
            
            # 텍스트 추출
            text = self._extract_text(html_content)
            
            return text
            
        except ValueError:
            raise
        except requests.RequestException as e:
            raise requests.RequestException(f"HTTP 요청 실패: {str(e)}")
        except Exception as e:
            raise Exception(f"HTML 파일 읽기 중 오류가 발생했습니다: {str(e)}")
    
    def _is_valid_url(self, url: str) -> bool:
        """
        URL 유효성을 검사합니다.
        
        Args:
            url (str): 검사할 URL
            
        Returns:
            bool: 유효한 URL인지 여부
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _fetch_html(self, url: str) -> str:
        """
        URL에서 HTML 내용을 가져옵니다.
        
        Args:
            url (str): HTML URL
            
        Returns:
            str: HTML 내용
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
            
        except requests.RequestException as e:
            raise requests.RequestException(f"HTML 가져오기 실패: {str(e)}")
    
    def _extract_text(self, html_content: str) -> str:
        """
        HTML에서 텍스트를 추출합니다.
        
        Args:
            html_content (str): HTML 내용
            
        Returns:
            str: 추출된 텍스트
        """
        try:
            # BeautifulSoup으로 HTML 파싱
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 불필요한 태그 제거
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            # 텍스트 추출
            text = soup.get_text()
            
            return text
            
        except Exception as e:
            raise Exception(f"텍스트 추출 중 오류 발생: {str(e)}")
    
 