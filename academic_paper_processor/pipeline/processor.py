from typing import Dict, List, Optional
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import Graph
from pydantic import BaseModel, Field
import streamlit as st


class PaperMetadata(BaseModel):
    """Schema for paper metadata."""
    title: str = Field(description="The title of the paper")
    authors: List[str] = Field(description="List of authors")
    publication_date: str = Field(description="Publication date")
    abstract: str = Field(description="Paper abstract")


class ResearchContent(BaseModel):
    """Schema for research content."""
    methodology: str = Field(description="Research methodology")
    findings: List[str] = Field(description="Key research findings")
    keywords: List[str] = Field(description="Keywords")
    summary: str = Field(description="Generated summary")


class ContentProcessor:
    """Processes academic paper content using LLM."""

    def __init__(self):
       # credentials = st.secrets["gcp_api_key"]["GOOGLE_API_KEY"]
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-001", temperature=0)
        self.max_tokens = 1000000
        self.token_buffer = 2500

        # Initialize prompts


        self.analysis_prompt = PromptTemplate.from_template("""                                                              
                  Analyze the following academic paper and provide a structured extraction of all relevant information. 
                  Format your response exactly as shown below, maintaining all headers and structure.                   

                  Paper text:                                                                                           
                  {text}                                                                                                

                  Provide your analysis in this exact format:                                                           
                  ---METADATA---                                                                                        
                  Title: <paper title>                                                                                  
                  Authors: <author1>, <author2>, ...                                                                    
                  Date: <publication date in YYYY-MM-DD format>                                                                              
                  Abstract: <paper abstract>                                                                            

                  ---METHODOLOGY---                                                                                     
                  <detailed description of the research methodology>                                                    

                  ---FINDINGS---                                                                                        
                  - <finding1>                                                                                          
                  - <finding2>                                                                                          
                  - <finding3>                                                                                          
                  [list all key findings]                                                                               

                  ---KEYWORDS---                                                                                        
                  <keyword1>, <keyword2>, <keyword3>, <keyword4>, <keyword5>                                            
                  [5-7 relevant keywords]                                                                               

                  ---SUMMARY---                                                                                         
                  <A comprehensive 3-4 paragraph summary focusing on main contributions, methodology, and results>      
        """)

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in the text."""
        return (len(text) + 3)//4

    def truncate_to_token_limit(self, text: str) -> tuple[str, bool]:
        """
        Truncate text to fit within token limit while preserving important sections.
        Returns tuple of (truncated_text, was_truncated).
        """
        prompt_tokens = self.count_tokens(self.analysis_prompt.template)
        available_tokens = self.max_tokens - prompt_tokens - self.token_buffer
        current_tokens = self.count_tokens(text)

        if current_tokens <= available_tokens:
            return text, False

        result = text[:available_tokens*4]

        return result, True

    def analyze_content(self, text: str) -> tuple[PaperMetadata,ResearchContent]:
        """Analyze paper content using LLM."""
        text, was_truncated = self.truncate_to_token_limit(text)

        response = self.llm.invoke(self.analysis_prompt.format(text=text))
        # Parse the response into structured format
        content = response.content
        sections = content.split('---')[1:]  # Skip the first empty split
        # Split response into sections
        section_dict = {sections[i]: sections[i + 1].strip() for i in range(0, len(sections), 2)}

        # Parse metadata
        metadata_lines = section_dict['METADATA'].split('\n')
        metadata_fields = ["title","authors", "date", "abstract"]
        content_fields = ["methodology", "findings", "keywords", "summary"]
        metadata = {}
        for line in metadata_lines:
            if line.startswith('Title:'):
                metadata['title'] = line.replace('Title:', '').strip()
            elif line.startswith('Authors:'):
                authors_str = line.replace('Authors:', '').strip()
                metadata['authors'] = [a.strip() for a in authors_str.split(',')]
            elif line.startswith('Date:'):
                metadata['publication_date'] = line.replace('Date:', '').strip()
            elif line.startswith('Abstract:'):
                metadata['abstract'] = line.replace('Abstract:', '').strip()

         # Parse research content
        research_content = {
            'methodology': section_dict['METHODOLOGY'].strip(),
            'findings': [
                finding.strip('- ').strip()
                for finding in section_dict['FINDINGS'].split('\n')
                if finding.strip().startswith('-')
            ],
            'keywords': [
                keyword.strip()
                for keyword in section_dict['KEYWORDS'].split(',')
            ],
            'summary': section_dict['SUMMARY'].strip()
        }

        for field in metadata_fields:
            if field not in metadata:
                if field.upper() in section_dict:
                    metadata[field] = section_dict[field.upper()].strip()
                else:
                    metadata[field] = None

        for field in content_fields:
            if field not in research_content:
                if field.upper() in section_dict:
                    research_content[field] = section_dict[field.upper()].strip()
                else:
                    research_content[field] = None


        return (PaperMetadata(**metadata),ResearchContent(**research_content))