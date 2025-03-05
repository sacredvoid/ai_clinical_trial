# AI-Based Clinical Trial Matching System

## Project Overview

This project implements an advanced AI-powered system for matching patients with suitable clinical trials. By leveraging natural language processing, vector embeddings, and machine learning techniques, the system analyzes patient medical records and compares them against inclusion and exclusion criteria of active clinical trials to identify potential matches. This tool aims to streamline the clinical trial enrollment process, helping researchers, healthcare professionals, and patients find relevant trials more efficiently.

## Core Architecture

The system employs a multi-stage pipeline architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Data Ingestion │────▶│  Data Processing│────▶│ Vector Embedding│────▶│ Matching Engine │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │                       │
        ▼                       ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│ Clinical Trials │     │  Patient Data   │     │ ChromaDB Vector │     │ JSON Results    │
│    Web Scraper  │     │  SQLite Database│     │     Store       │     │                 │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Key Components

### 1. Data Ingestion & Storage

#### Patient Data Processing (`csv_to_db.py`)
- Converts patient CSV files into a structured SQLite relational database
- Cleans and normalizes column names for consistency
- Creates tables for different types of patient data (allergies, conditions, medications, etc.)
- Provides a queryable foundation for patient information

#### Clinical Trial Web Scraper (`web_scraper_trials.py`)
- Asynchronously scrapes clinical trial data from clinicaltrials.gov
- Extracts NCT IDs, titles, inclusion criteria, and exclusion criteria
- Implements pagination handling, retry mechanisms, and progress tracking
- Stores processed trial data in ChromaDB for vector similarity searching

### 2. Data Processing & Summarization

#### Patient Profile Creation (`combine_patient_data.py`)
- Consolidates patient information from multiple database tables
- Creates comprehensive patient profiles with relevant medical history
- Calculates patient age and formats data for LLM processing
- Provides a unified view of each patient's health status

#### LLM Summarization Pipeline (`summarize_apis/`)
- Connects to language model APIs (Hugging Face, OpenRouter)
- Summarizes complex patient data into concise, structured profiles
- Processes clinical trial criteria for better matching
- Supports multiple LLM providers with a consistent interface

### 3. Vector Embedding & Storage

#### Embedding Generation (`create_clinical_trial_embeddings.py`)
- Creates vector embeddings for patient profiles and clinical trial criteria
- Uses SentenceTransformer models for semantic representation
- Maintains separate collections for inclusion and exclusion criteria
- Enables efficient similarity searching and comparison

### 4. Matching Algorithm (`find_matching_trial.py`)

The matching process employs a sophisticated 3-stage algorithm:

1. **Vector Similarity Search**:
   - Embeds patient profiles using SentenceTransformer
   - Calculates cosine similarity between patient embeddings and trial criteria embeddings
   - Scores trials based on similarity to inclusion criteria and dissimilarity to exclusion criteria
   - Filters trials with scores above a defined threshold

2. **Expert LLM Assessment**:
   - For top-scoring trials, performs detailed eligibility analysis using LLM
   - Evaluates patient data against specific inclusion/exclusion criteria
   - Generates eligibility scores and detailed reasoning
   - Provides human-readable explanations for match quality

3. **Result Generation**:
   - Compiles matching trials and their assessments into structured JSON format
   - Includes trial IDs, names, and detailed eligibility criteria matches
   - Saves results for each patient for further analysis or integration

## Technical Implementation Details

### Data Flow

1. Patient data from CSV files is processed and stored in a SQLite database
2. Clinical trial data is scraped from clinicaltrials.gov and stored in ChromaDB
3. Patient profiles are created by querying the SQLite database
4. LLM summarizes patient profiles and trial criteria
5. Vector embeddings are generated for patient profiles and trial criteria
6. The matching algorithm identifies suitable trials for each patient
7. Results are saved as JSON files

### Key Technologies

- **Database**: SQLite with SQLAlchemy ORM
- **Web Scraping**: AsyncWebCrawler with retry mechanisms
- **Vector Database**: ChromaDB for efficient similarity searching
- **Embeddings**: SentenceTransformer (all-MiniLM-L6-v2)
- **Language Models**: Llama 3.2 3B-Instruct via Hugging Face/OpenRouter APIs
- **Data Processing**: Pandas for CSV handling and data manipulation
- **Asynchronous Processing**: Python asyncio for concurrent operations

## Features

- [x] **Web Scraper**: Fetches the latest ongoing clinical trials from clinicaltrials.gov and stores them as vector embeddings in ChromaDB
- [x] **Patient Data Preprocessing**: Converts CSV files into a structured SQLite database for efficient querying
- [x] **LLM Pipeline for Summarization**: Connects to local or online LLM APIs to summarize patient data and trial criteria
- [x] **Matching Algorithm**: Implements a 3-stage matching process combining vector similarity, LLM assessment, and threshold filtering
- [x] **Documentation**: Provides comprehensive documentation of the system architecture and components
- [x] **JSON File Output**: Generates structured output files containing matching trials and eligibility assessments
- [ ] **Unit and Integration Tests**: Test suite for ensuring reliability and accuracy
- [ ] **Google Sheet Output**: Export functionality for collaborative review

## Setting Up the Environment

1. **Create a virtual environment:**

   **Using pip:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux or macOS
   venv\Scripts\activate  # On Windows
   ```

   **Using conda:**
   ```bash
   conda create -n myenv python=3.9
   conda activate myenv
   ```

2. **Install dependencies:**

   **Using pip:**
   ```bash
   pip install -r requirements.txt
   ```

   **Using conda:**
   ```bash
   conda env create -f environment.yml
   conda activate myenv
   ```

## Running the System

1. **Obtain API Keys:**
   - Get a Hugging Face API key from [huggingface.co](https://huggingface.co/)
   - Store it in a `.env` file as `HUGGINGFACE_KEY={yourkey}`
   - Alternatively, you can use OpenRouter by obtaining a key and setting `OPENROUTER_KEY={yourkey}`

2. **Prepare Sample Data:**
   - Download sample patient data from [here](https://mitre.box.com/shared/static/aw9po06ypfb9hrau4jamtvtz0e5ziucz.zip)
   - Extract to the project root directory and rename to `patient_data`

3. **Run the Main Script:**
   ```bash
   python main.py
   ```
   This will:
   - Set up the patient SQLite database
   - Scrape clinical trials and store them in ChromaDB
   - Run the matching algorithm
   - Save results as JSON files in `patient_trials_matched/`

4. **Adjust Processing Parameters (Optional):**
   - Modify `find_matching_trial.py` to change the number of patients processed
   - Update `web_scraper_trials.py` to adjust the number of trials scraped

## Technical Limitations

1. **LLM API Rate Limits:**
   The system relies on external LLM APIs which have rate limits. This restricts the number of patients and trials that can be processed in a given time period. Consider using paid API plans or implementing caching mechanisms for production use.

2. **Context Window Constraints:**
   The Llama 3.2 3B-Instruct model has a context window of 4096 tokens, limiting the amount of patient data and trial information that can be processed simultaneously. This may affect the comprehensiveness of the analysis, particularly for complex medical histories or detailed trial criteria.

3. **LLM Output Variability:**
   Despite prompt engineering, LLM outputs can vary, affecting the consistency of matching results. This variability is inherent to current language models and can impact the reliability of the eligibility assessments.

4. **Embedding Model Limitations:**
   The system uses a relatively small embedding model (all-MiniLM-L6-v2) which, while efficient, may not capture all the nuances of medical terminology and relationships compared to larger domain-specific models.

## Future Improvements

1. **Enhanced LLM Integration:**
   - Implement larger models like GPT-4, Claude 3 Opus, or Llama 3.2 70B for more accurate analysis
   - Explore medical domain-specific fine-tuned models for improved understanding of clinical terminology

2. **Advanced Embedding Techniques:**
   - Implement keyword extraction before embedding generation
   - Use larger, medical domain-specific embedding models
   - Explore hybrid retrieval approaches combining sparse and dense embeddings

3. **Refined Matching Algorithm:**
   - Optimize the weighting between inclusion and exclusion criteria similarity
   - Implement more sophisticated scoring mechanisms that account for the importance of different criteria
   - Develop a feedback loop to improve matching accuracy over time

4. **System Robustness:**
   - Add comprehensive test suite for all components
   - Implement caching and rate-limiting strategies for API calls
   - Develop monitoring and logging for production deployment

5. **User Interface:**
   - Create a web interface for easier interaction with the system
   - Implement visualization tools for match results
   - Develop export functionality to various formats (CSV, Excel, Google Sheets)

6. **Domain-Specific Customization:**
   - Fine-tune models on medical literature and clinical trial data
   - Implement specialized processing for different medical specialties
   - Develop custom prompts for different types of clinical trials

## License

This project is licensed under the MIT License.
