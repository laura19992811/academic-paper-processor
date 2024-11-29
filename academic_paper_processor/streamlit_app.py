import streamlit as st
import pandas as pd
from google.cloud import bigquery
from pathlib import Path
import tempfile
from pipeline import AcademicPaperPipeline
from google.oauth2 import service_account

# Initialize BigQuery client
credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"])
client = bigquery.Client(credentials=credentials)
PROJECT_ID = st.secrets["gcp"]["project_id"]
DATASET_ID = st.secrets["gcp"]["dataset_id"]
TABLE_ID = st.secrets["gcp"]["table_id"]

def save_uploaded_file(uploaded_file):
    """Save uploaded file temporarily and return the path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def process_paper(file_path):
    """Process a single paper through the pipeline"""


    pipeline = AcademicPaperPipeline(project_id=PROJECT_ID, dataset_id=DATASET_ID,table_id=TABLE_ID)
    return pipeline.process_document(pdf_path=file_path)

def fetch_recent_papers():
    """Fetch recently processed papers from BigQuery"""
    query = f"""
    SELECT 
        paper_id,
        title,
        authors,
        publication_date,
        keywords
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    ORDER BY created_at DESC
    LIMIT 10
    """
    return client.query(query).to_dataframe()

def main():
    st.set_page_config(page_title="Academic Paper Analyzer", layout="wide")

    st.title("📚 Academic Paper Analysis Pipeline")

    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Upload Paper", "View Recent Papers", "Search Papers"]
    )

    if page == "Upload Paper":
        st.header("Upload New Paper")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if uploaded_file:
            with st.spinner("Processing paper..."):
                # Save uploaded file
                temp_path = save_uploaded_file(uploaded_file)

                try:
                    # Process the paper
                    results = process_paper(temp_path)

                    # Display results in tabs
                    tab1, tab2, tab3 = st.tabs(["Basic Info", "Analysis", "Summary"])

                    with tab1:
                        st.subheader("Paper Information")
                        st.write(f"**Title:** {results['title']}")
                        st.write(f"**Authors:** {', '.join(results['authors'])}")
                        st.write(f"**Publication Date:** {results['publication_date']}")
                        st.write(f"**Keywords:** {', '.join(results['keywords'])}")

                    with tab2:
                        st.subheader("Research Analysis")
                        st.write("**Methodology:**")
                        st.write(results['methodology'])
                        st.write("**Key Findings:**")
                        for idx, finding in enumerate(results['findings'], 1):
                            st.write(f"{idx}. {finding}")

                    with tab3:
                        st.subheader("Paper Summary")
                        st.write(results['summary'])

                finally:
                    # Clean up temporary file
                    Path(temp_path).unlink()

    elif page == "View Recent Papers":
        st.header("Recently Processed Papers")


        df = fetch_recent_papers()

        # Display papers in an expandable format
        for _, row in df.iterrows():
            with st.expander(f"📄 {row['title']}"):
                st.write(f"**Authors:** {', '.join(row['authors'])}")
                st.write(f"**Publication Date:** {row['publication_date']}")
                st.write(f"**Keywords:** {', '.join(row['keywords'])}")

                # Add button to view full details
                if st.button("View Full Details", key=row['paper_id']):
                    # Fetch and display complete paper details
                    full_details = client.query(f"""
                        SELECT *
                        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
                        WHERE paper_id = '{row['paper_id']}'
                    """).to_dataframe().iloc[0]

                    st.write("**Abstract:**")
                    st.write(full_details['abstract'])
                    st.write("**Summary:**")
                    st.write(full_details['summary'])




    else:  # Search Papers
        st.header("Search Papers")

        # Search options
        search_type = st.selectbox(
            "Search by",
            ["Title", "Author", "Keywords", "Full Text"]
        )

        search_term = st.text_input("Enter search term")

        if search_term:
            # Construct and execute search query based on search type
            query = f"""
            SELECT 
                paper_id,
                title,
                authors,
                publication_date,
                keywords
            FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
            WHERE 
            """

            if search_type == "Title":
                query += f"LOWER(title) LIKE LOWER('%{search_term}%')"
            elif search_type == "Author":
                query += f"EXISTS (SELECT 1 FROM UNNEST(authors) AS author WHERE LOWER(author) LIKE LOWER('%{search_term}%'))"
            elif search_type == "Keywords":
                query += f"EXISTS (SELECT 1 FROM UNNEST(keywords) AS keyword WHERE LOWER(keyword) LIKE LOWER('%{search_term}%'))"
            else:  # Full Text
                query += f"""
                LOWER(CONCAT(
                    title,
                    abstract,
                    methodology,
                    summary
                )) LIKE LOWER('%{search_term}%')
                """

            results = client.query(query).to_dataframe()

            if len(results) > 0:
                st.write(f"Found {len(results)} papers:")
                for _, row in results.iterrows():
                    with st.expander(f"📄 {row['title']}"):
                        st.write(f"**Authors:** {', '.join(row['authors'])}")
                        st.write(f"**Publication Date:** {row['publication_date']}")
                        st.write(f"**Keywords:** {', '.join(row['keywords'])}")
            else:
                st.write("No papers found matching your search criteria.")

if __name__ == "__main__":
    main()