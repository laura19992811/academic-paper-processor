# Academic Paper Processing Pipeline

A document processing pipeline that leverages LangGraph, Large Language Models, and Google Cloud Services to extract and analyze academic papers. The pipeline performs structured information extraction, research findings analysis, and stores results in BigQuery.

## Features
### Streamlit App Features
- **Uploading PDF**: Uploading PDF files from your system to the model through the streamlit app 
- **Recent PDF**: Seeing a summary or detailed information about the recently processed PDFs
- **Search PDF**: Find previously processed PDFs by certain features like title or author.

### Pipeline Features
- **PDF Text Extraction**: Automatically extracts text from academic papers uploaded on PDF
- **Structured Information Extraction**: 
  - Title and authors
  - Publication date
  - Abstract
  - Research methodology
- **Content Analysis**:
  - Key research findings identification
  - Methodology extraction
  - Keyword generation
  - Automated summary generation
- **Data Storage**: Integrated BigQuery storage for extracted information




## Prerequisites

- Python 3.12 
- Google Cloud account with BigQuery user access
- Google API Key
- A PDF document to process
- pipenv

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/academic-paper-processor
cd academic-paper-processor
```

2. Create and activate virtual environment with pipenv:
```bash
mkdir .venv #To create your virtual environment in the local directory
pipenv install
pipenv shell
```

## Configuration
1. Include your GOOGLE_API_KEY as well as the information from your GOOGLE_APPLCIATION_CREDENTIALS json file to the ./streamlit/secrets.toml file so that these are accessible to the streamlit app as follows:
```bash
GOOGLE_API_KEY="your_api_key"

[gcp_service_account]
type = "service_account"
project_id=  "*"
private_key_id= "*"
private_key= "*"
client_email= "*"
client_id="*"
auth_uri= "*"
token_uri= "*"
auth_provider_x509_cert_url= "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url= "*"
universe_domain="googleapis.com"
```
In case you wish to run the pipeline components outside the streamlit app you can set up the environment variables
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
export GOOGLE_API_KEY="your_api_key"
```
2. Create your project and dataset in BigQuery, afterwards insert the name of the project and dataset into secrets.toml file as well as the name of the table in which you wish to store the processed data.
```bash
[gcp]
project_id = "your_project_id"
dataset_id = "your_dataset_id"
table_id = "your_table_id"
```
## Usage
### Running the streamlit app
```bash
 streamlit run .\academic_paper_processor\streamlit_app.py
```

### Running the Pipeline

```python
from pipeline import AcademicPaperPipeline

# Initialize pipeline
pipeline = AcademicPaperPipeline(project_id="your_project_id", dataset_id="your_dataset_id",table_id="your_table_id") 

# Process a single document
results = pipeline.process_document("path/to/paper.pdf")

# Print results
print(f"Title: {results['title']}")
print(f"Authors: {', '.join(results['authors'])}")
print(f"Keywords: {', '.join(results['keywords'])}")
```



## Project Structure

```
academic-paper-processor/
├── academic_paper_processor/
│   ├── pipeline/
│   │   ├── extractors.py  # PDF extraction logic
│   │   ├── processors.py  # Content processing
│   │   └── storage.py     # BigQuery integration
│   └── streamlit_app.py
└── .streamlit/
    └── secrets.toml
```

## Pipeline Components

1. **PDFExtractor**: Handles PDF document ingestion and text extraction
2. **ContentProcessor**: Processes academic content using LLMs
3. **BigQueryStorage**: Manages data persistence in Google BigQuery
4. **LangGraph Pipeline**: Orchestrates the entire processing workflow




## Authors

Laura Daniela Torralba Garcia - [YourGithub](https://github.com/laura19992811)

## Acknowledgments

- LangChain and LangGraph teams
- Google Cloud Platform
- Python PDF processing community