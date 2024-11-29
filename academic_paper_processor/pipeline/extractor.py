from typing import Dict, List, Optional
import PyPDF2
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import re


class PDFExtractor:
    """Handles the extraction of text from PDF documents."""

    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return self._clean_text(text)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace and artifacts."""
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove hyphenation at line breaks
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        return text.strip()