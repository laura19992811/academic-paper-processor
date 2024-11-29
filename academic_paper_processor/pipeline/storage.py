from google.cloud import bigquery
from datetime import datetime
import uuid
from .processor import PaperMetadata,ResearchContent
import streamlit as st
from google.oauth2 import service_account

class BigQueryStorage:
    """Handles storage of processed paper data in BigQuery."""

    def __init__(self, project_id: str, dataset_id: str, table_id:str):
        credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"])
        self.client = bigquery.Client(credentials=credentials)
        self.table_id = f"{project_id}.{dataset_id}.{table_id}"

        # Ensure table exists
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self):
        """Create the papers table if it doesn't exist."""
        schema = [
            bigquery.SchemaField("paper_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("authors", "STRING", mode="REPEATED"),
            bigquery.SchemaField("publication_date", "DATE"),
            bigquery.SchemaField("abstract", "STRING"),
            bigquery.SchemaField("methodology", "STRING"),
            bigquery.SchemaField("findings", "STRING", mode="REPEATED"),
            bigquery.SchemaField("keywords", "STRING", mode="REPEATED"),
            bigquery.SchemaField("summary", "STRING"),
            bigquery.SchemaField("created_at", "TIMESTAMP"),
        ]

        #table_id = "your-project.your_dataset.your_table_name"
        table = bigquery.Table(self.table_id, schema=schema)
        table = self.client.create_table(table, exists_ok=True)

    def store_paper(self, metadata: PaperMetadata, content: ResearchContent):
        """Store processed paper data in BigQuery."""
        rows_to_insert = [{
            "paper_id": str(uuid.uuid4()),
            "title": metadata.title,
            "authors": metadata.authors,
            "publication_date": metadata.publication_date,
            "abstract": metadata.abstract,
            "methodology": content.methodology,
            "findings": content.findings,
            "keywords": content.keywords,
            "summary": content.summary,
            "created_at": datetime.utcnow().isoformat()
        }]

        errors = self.client.insert_rows_json(self.table_id, rows_to_insert)
        if errors:
            raise Exception(f"Errors inserting rows: {errors}")