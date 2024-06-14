from abc import ABC, abstractmethod
from PyPDF2 import PdfReader
from docx import Document

'''
Module designed to handle different types of inputs, namely: PDF, txt and docx documents.

'''

class InputHandler(ABC):
    '''
    Base class for handlers 
    '''

    @abstractmethod
    def read_file(self, file):
        """
        Args:
            file (Uploaded file): The file to be read
        """
        pass 
    

class PDFHandler(InputHandler):
    """File hander for PDF documents"""
    
    def read_file(self, file):
        """ Read inputed file 
        Args:
            file (Uploaded file): The file to be read
            
        Returns:
            str 
        
        """
        
        try: 
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                    
            return text
        
        except Exception as e:
            print(f"Failed to read PDF file: {e}")
            return ""
        
        
        
class FileHandlerFactory:
    """Factory for creating file handlers based on file type."""

    @staticmethod
    def get_file_handler(file_type):
        """Get the appropriate file handler for the given file type.

        Parameters:
        file_type (str): The MIME type of the file.

        Returns:
        FileHandler: The appropriate file handler.

        Raises:
        ValueError: If the file type is not supported.

        """
        if file_type == "application/pdf":
            return PDFHandler()
        # elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        #     return DocxHandler()
        # elif file_type == "text/plain":
        #     return TxtHandler()
        # elif file_type == "text/csv":
        #     return CSVFileHandler()
        # else:
        #     raise ValueError("Invalid file type")