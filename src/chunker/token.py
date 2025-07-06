from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TokenSizeChunker:
    """텍스트를 청킹하는 클래스"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        """
        TokenSizeChunker 초기화
        
        Args:
            chunk_size (int): 청크 크기 (기본값: 1000)
            chunk_overlap (int): 청크 간 겹침 크기 (기본값: 200)
            separators (Optional[List[str]]): 분리자 목록 (기본값: None)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators
        
        # RecursiveCharacterTextSplitter 초기화
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators
        )
    
    def __call__(self, text: str, metadata: Optional[dict] = None) -> List[dict]:
        """
        텍스트를 청킹하여 Document 리스트로 반환합니다.
        
        Args:
            text (str): 청킹할 텍스트
            metadata (Optional[dict]): 메타데이터
            
        Returns:
            List[Document]: 청킹된 Document 리스트
        """
        try:
            # 텍스트 청킹
            chunks = self.text_splitter.split_text(text)
            
            # Document 객체 생성
            documents = []
            for i, chunk in enumerate(chunks):
                # 기본 메타데이터 설정
                doc = {
                    "content": chunk,
                    "chunk_order": i,
                }
                
                # 사용자 메타데이터 추가
                if metadata:
                    doc.update(metadata)
                
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            raise Exception(f"텍스트 청킹 중 오류가 발생했습니다: {str(e)}")
    
    def split_text(self, text: str) -> List[str]:
        """
        텍스트를 청킹하여 문자열 리스트로 반환합니다.
        
        Args:
            text (str): 청킹할 텍스트
            
        Returns:
            List[str]: 청킹된 텍스트 리스트
        """
        try:
            return self.text_splitter.split_text(text)
            
        except Exception as e:
            raise Exception(f"텍스트 청킹 중 오류가 발생했습니다: {str(e)}")