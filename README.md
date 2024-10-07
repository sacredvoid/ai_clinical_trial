# AI Based Clinical-Trial Matching

Project done as a take-home assessment for Turmerik.

## Project Overview

This project implements a matching algorithm that takes patient data as input and outputs a list of clinical trials that each patient is eligible for. The algorithm considers various patient attributes and compares them against the inclusion and exclusion criteria of active clinical trials.

## Feature Review
- [x] Web scraper to fetch the latest ongoing trials - Store Trial Data as Vector Store in ChromaDB
- [x] Preprocess all available patient data - Store into SQLite DB
- [x] LLM Pipeline to Summarize given text - Connects to local/online LLM APIs
- [x] Matching Algorithm - 3 Stage Matching
- [x] Documentation
- [x] JSON File Output 
- [ ] Unit and Integration Tests
- [ ] Google Sheet file output


## Setting up environment
1. Create your virtual environment, either pip/conda.
2. Run `pip install -r requirements.txt` or `conda env create -f environment.yml`

## Steps to run
1. Get a Huggingface API Key. Store it in a `.env` file as `HUGGINGFACE_KEY={yourkey}`. All other keys will be stored here for use in LLM APIs.
2. Download the sample data from [here](https://mitre.box.com/shared/static/aw9po06ypfb9hrau4jamtvtz0e5ziucz.zip) and move it to the github repo's root directory. Rename dir to `patient_data` which contains all .csv files.
3. Run `python main.py`. This should setup the patients SQLite DB, scrape clinical trials and store in ChromaDB, run the matching algorithm and store it in a dir as JSONs for each patient.
4. Feel free to edit limits (in `find_matching_trial.py`) set since the number of patients, trials are into thousands, I run it for a small sample of them.

## Limitations
1. LLM API Rate Limits
2. Did not use all the columns like dates of patient data due to the context window of the free LLM used (LLama 3.2 3B-Instruct) under 4096 tokens. Having more information for the LLM like dates is important in a lot of the clinical trials.
3. The output of the LLM is varying, even after prompt engineering and referring to the prompt used in the [research paper](https://arxiv.org/pdf/2402.05125). The model is also 3B params, the paper used GPT4 which is very huge. Having access to larger models will make the process of matching more efficient.
4. Did not have time to add tests, this was one of the biggest take-home assessments I've ever done and very rewarding as I got to learn a lot.

## Future Improvements
1. Use a bigger and better LLM, like GPT-4, o1, Llama 3.2 70b etc to get better analysis. Also checkout Medical Finetuned LLMs and see how they perform.
2. Use keyword extractors on patient data and clinical trial data and then create embeddings.
3. Use a bigger and better embedding model. Currently using the smallest and best that could run on my system.
4. Think of a better way to pick the best trials based on inclusion/exclusion criteria's embeddings. Currently using a combination of min distance to inclusion criteria and max distance to exclusion criteria (equal weightage). Maybe play around with that to get better results.
5. Finetune your own LLM model, unsure if data is readily available.
6. Prompt engineering works better for bigger models, I tried it for Llama 3.2 1B-instruct, and it did really well!
7. Add tests wherever possible, make some modules and pipelines better.

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

Your code implements a matching algorithm that identifies clinical trials suitable for patients based on their health profiles and trial inclusion/exclusion criteria. Here’s a summary focusing on the matching algorithm:

### Summary of the Matching Algorithm

1. **Patient Profile Creation**: 
   - For each patient, the algorithm checks if a profile already exists in the database. If not, it creates a patient profile by summarizing relevant health information using an API call to a language model.

2. **Embeddings Generation**: 
   - The summarized patient profile is embedded using a pre-trained SentenceTransformer model. This embedding captures the essential features of the patient’s health data.

3. **Similarity Calculation**: 
   - The algorithm retrieves embeddings of clinical trials from two collections: one for inclusion criteria and another for exclusion criteria. 
   - It calculates cosine similarity between the patient’s embedding and each trial’s inclusion and exclusion embeddings to evaluate how closely they match.

4. **Scoring Trials**: 
   - A score is computed for each trial based on the similarity of the inclusion and exclusion embeddings to the patient’s profile. 
   - If the inclusion similarity is high and the exclusion similarity is low, the trial receives a positive score.

5. **Threshold Filtering**: 
   - Trials with a score above a defined threshold are considered potentially compatible. The top N trials are selected based on their scores.

6. **Expert LLM Assessment**: 
   - For each selected trial, the algorithm uses another language model to analyze the inclusion and exclusion criteria against the patient’s profile and generate a detailed eligibility assessment. 
   - This includes determining the eligibility score (0-1) and providing reasoning based on the patient's health status.

7. **Output**: 
   - The matching trials and their eligibility assessments are compiled into a JSON format and saved for later use.

### Key Points
- The algorithm combines embeddings and similarity metrics to efficiently find matching trials.
- It incorporates AI-driven summarization and eligibility assessment to refine the matching process.
- The method is designed to be scalable while adhering to API rate limits by processing a limited number of patients at a time. 

This structure allows for flexible and efficient querying of clinical trials based on personalized patient data.

## License

This project is licensed under the MIT License.
