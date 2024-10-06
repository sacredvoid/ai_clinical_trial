# AI Based Clinical-Trial Matching

Project done as a take-home assessment for Turmerik.

## Project Overview

This project implements a matching algorithm that takes patient data as input and outputs a list of clinical trials that each patient is eligible for. The algorithm considers various patient attributes and compares them against the inclusion and exclusion criteria of active clinical trials.

## Feature Review
- [x] Web scraper to fetch the latest ongoing trials - Store Trial Data as Vector Store in ChromaDB
- [x] Preprocess all available patient data - Store into SQLite DB
- [x] LLM Pipeline to Summarize given text - Connects to local/online LLM APIs
- [x] Matching Algorithm - 3 Stage Matching
- [ ] Unit and Integration Tests
- [x] Documentation - Mostly done

## Setting up environment
1. Create your virtual environment, either pip/conda.
2. Run `pip install -r requirements.txt` or `conda env create -f environment.yml`

## Components
### Patient Data CSVs to SQLite RDB
Run `python csv_to_db.py`. Here's what it does:
1. Creates a SQLite database named 'patient_data.db' using SQLAlchemy.
2. Processes CSV files from a directory named 'patient_data':
    - Reads each CSV file using pandas.
    - Cleans column names by converting to lowercase and replacing spaces and hyphens with underscores.
    - Creates a table in the SQLite database for each CSV file, using the filename (without extension) as the table name.
    - Imports the data from each CSV into its corresponding table.

3. Prints confirmation messages for each imported file.
4. After importing all files, it uses SQLAlchemy's inspect function to print the structure of each table in the database, showing column names and their data types.

### Web Scraper - Clinical Trials
Run `python web_scraper_trials.py`. Here's why:<br>
This script performs the following main tasks:

1. **Web Scraping**: 
   - Scrapes clinical trial data from clinicaltrials.gov
   - Extracts NCT IDs and trial details

2. **Data Processing**:
   - Extracts specific information like title, inclusion, and exclusion criteria
   - Uses regular expressions for text extraction

3. **Data Storage**:
   - Stores processed data in a ChromaDB vector database
   - Creates embeddings for efficient searching

**Features**:

- Asynchronous web crawling for improved performance
- Pagination handling to scrape multiple pages
- Retry mechanism for failed requests
- Progress bar to track scraping progress
- Checks for existing entries to avoid duplicates
- Error handling and logging of failed scrapes


The script is configured to scrape a specified number of pages and trials per page. It then processes this data and stores it in a local ChromaDB vector store for further analysis or retrieval.

### Find Matching Trial

This script is designed to match patients with suitable clinical trials based on their medical profiles. Here's a summary of its main functions:

1. It uses a pre-trained sentence transformer model to create embeddings for patient profiles and clinical trial data.

2. The script interacts with a ChromaDB database to store and retrieve clinical trial information.

3. The main function, `find_matching_trials_per_patient`, takes a patient ID and performs the following steps:
   - Creates a patient profile from various data sources
   - Summarizes the patient profile using an external API (OpenRouter)
   - Converts the summarized profile into an embedding
   - Queries the ChromaDB to find the most similar clinical trials based on vector similarity

4. There's a function `find_matching_trials_for_all` that applies the matching process to multiple patients, limited to 10 due to API rate limits.

5. The script uses external functions for creating patient profiles and getting patient IDs.

Overall, this script automates the process of finding relevant clinical trials for patients by leveraging natural language processing and vector similarity search techniques.


## License

This project is licensed under the MIT License.
