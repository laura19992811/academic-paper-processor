from typing import Dict,Any
import tempfile
from pathlib import Path
from langgraph.graph import Graph
from .extractor import *
from .processor import *
from .storage import *
from langgraph.graph import Graph, END, START
from pydantic import BaseModel


# Define the state type that will be passed between nodes
class GraphState(BaseModel):
    pdf_path: str
    text: str = ""
    metadata: Dict = {}
    content: Dict = {}
    stored: bool = False

class AcademicPaperPipeline:
    """Main pipeline class orchestrating the document processing workflow."""

    def __init__(self, project_id: str = "your-project", dataset_id: str = "your-dataset", table_id: str = "your-table"):
        self.pdf_extractor = PDFExtractor()
        self.content_processor = ContentProcessor()
        self.storage = BigQueryStorage(project_id, dataset_id,table_id)
        self.graph = self._build_graph()

    def _build_graph(self) -> Graph:
        """Build the LangGraph processing pipeline."""
        graph = Graph()

        # Define node functions that work with the state
        def extract_text(state: GraphState) -> GraphState:
            """Extract text from PDF."""
            text = self.pdf_extractor.extract_text(state.pdf_path)
            return GraphState(
                pdf_path=state.pdf_path,
                text=text
            )

        def process_content(state: GraphState) -> GraphState:
            """Process the extracted text."""
            metadata, content = self.content_processor.analyze_content(state.text)
            return GraphState(
                pdf_path=state.pdf_path,
                text=state.text,
                metadata=metadata.dict(),
                content=content.dict()
            )

        def store_results(state: GraphState) -> GraphState:
            """Store the processed results."""
            self.storage.store_paper(
                PaperMetadata(**state.metadata),
                ResearchContent(**state.content)
            )
            return GraphState(
                pdf_path=state.pdf_path,
                text=state.text,
                metadata=state.metadata,
                content=state.content,
                stored=True
            )

        # Add nodes
        graph.add_node("extract_text", extract_text)
        graph.add_node("process_content", process_content)
        graph.add_node("store_results", store_results)

        # Define edges
        graph.add_edge(START, "extract_text")
        graph.add_edge("extract_text", "process_content")
        graph.add_edge("process_content", "store_results")
        graph.add_edge("store_results", END)

        graph = graph.compile()
        return graph

    def process_document(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a single document using direct graph invocation.
        """
        # Create initial state as a GraphState object
        initial_state = GraphState(pdf_path=pdf_path)

        # Invoke the graph with the initial state
        final_state = self.graph.invoke(initial_state)

        # Return combined results
        return {
            **final_state.metadata,
            **final_state.content,
            "processed_file": final_state.pdf_path,
            "stored": final_state.stored
        }