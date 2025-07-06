import os
import fitz  # PyMuPDF


class PDFReader:
    """PDF 파일을 읽고 텍스트를 추출하는 클래스"""
    
    def __init__(self):
        """PDFReader 초기화"""
        pass
    
    def __call__(self, file_path: str) -> str:
        """
        PDF 파일을 읽고 텍스트를 추출합니다.
        
        Args:
            file_path (str): PDF 파일 경로
            
        Returns:
            str: 추출된 텍스트
            
        Raises:
            FileNotFoundError: 파일이 존재하지 않을 경우
            ValueError: PDF 파일이 아닐 경우
            Exception: 기타 오류 발생 시
        """
        try:
            # 파일 존재 여부 확인
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
            
            # PDF 파일 여부 확인
            if not file_path.lower().endswith('.pdf'):
                raise ValueError(f"PDF 파일이 아닙니다: {file_path}")
            
            # 텍스트 추출
            text = self._extract_text(file_path)
            
            return text
            
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"PDF 파일 읽기 중 오류가 발생했습니다: {str(e)}")
    
    def _extract_text(self, file_path: str) -> str:
        """
        PDF 파일에서 텍스트를 추출합니다.
        
        Args:
            file_path (str): PDF 파일 경로
            
        Returns:
            str: 추출된 텍스트
        """
        text = ""
        
        try:
            # PDF 문서 열기
            doc = fitz.open(file_path)
            
            # 모든 페이지에서 텍스트 추출
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                text += page_text + "\n"
            
            # 문서 닫기
            doc.close()
            
        except Exception as e:
            raise Exception(f"텍스트 추출 중 오류 발생: {str(e)}")
        
        return text
