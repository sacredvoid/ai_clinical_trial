import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from collections import defaultdict
from tenacity import retry, stop_after_attempt, wait_exponential
import os
from tqdm import tqdm
from create_clinical_trial_embeddings import init, embed_and_add_single_entry, check_id_exists

async def extract_nct_ids(crawler, trials_per_page=25, page_number=1):
    # Define the extraction schema
    schema = {
        "name": "Clinical Trial NCT IDs",
        "baseSelector": ".ng-star-inserted",
        "fields": [
            {
                "name": "nct_id",
                "selector": ".nctCell",
                "type": "text"
            }
        ]
    }

    js_code = """
    (async () => {
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(resolve => setTimeout(resolve, 2000));  // Wait for 2 seconds
    })();
    """

    # Create the extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

    # Use the AsyncWebCrawler with the extraction strategy
    result = await crawler.arun(
        url=f"https://clinicaltrials.gov/search?viewType=Table&aggFilters=status:rec&limit={trials_per_page}&page={page_number}",
        extraction_strategy=extraction_strategy,
        js_code=js_code,
        verbose=False
    )

    assert result.success, "Failed to crawl the page"
    # Parse the extracted content
    extracted_data = json.loads(result.extracted_content)
    # Parse JSON and go to the extracted page
    id_set = set(id['nct_id'] for id in extracted_data)
    return id_set

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_trial_details_by_id(crawler, trial_id):
    
    trial_page_schema = {
        "name": "Clinical Trial Data",
        "baseSelector": "div.content",
        "fields": [
            {
                "name": "Study Overview",
                "selector": "div#study-overview",
                "type": "text"
            },
            {
                "name": "Participation Criteria",
                "selector": "#participation-criteria > ctg-participation-criteria:nth-child(2)",
                "type": "text"
            }
        ]
    }

    extraction_strategy = JsonCssExtractionStrategy(trial_page_schema, verbose=True)
    # print("Processing: ",trial_id," #################")
    
    js_code = """
    window.onload = async () => {
    };
    """

    trial_details_per_id = await crawler.arun(
                            url=f"https://clinicaltrials.gov/study/{trial_id}",
                            extraction_strategy=extraction_strategy,
                            verbose=False,
                            js_code=js_code
                            )
    if not trial_details_per_id.success:
        print("Failed to crawl the page")

    try:
        return json.loads(trial_details_per_id.extracted_content)[0]
    except Exception as e:
        pass

def write_to_json(filename, data):
    save_dir = './clinical_trial_data'
    os.makedirs(save_dir, exist_ok=True)
    file_save_path = os.path.join(save_dir, filename)

    with open(file_save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # print(f"Written file {file_save_path}")

def extract_title(data):
    match = re.search(r'Official Title(.*)Conditions', data)
    if match:
        official_title = match.group(1).strip()
        # print(official_title)
        return official_title
    else:
        # print("Official Title not found")
        return data

def extract_inclusion_criteria(data):
    inclusion_match = re.search(r'Inclusion Criteria:(.*)Exclusion Criteria:', data, re.DOTALL)
    if inclusion_match:
        inclusion_criteria = inclusion_match.group(1).strip()
        # print("Inclusion Criteria:\n", inclusion_criteria)
        return inclusion_criteria
    else:
        return data
    
def extract_exclusion_criteria(data):
    exclusion_match = re.search(r'Exclusion Criteria:(.*)', data, re.DOTALL)
    if exclusion_match:
        exclusion_criteria = exclusion_match.group(1).strip()
        # print("\nExclusion Criteria:\n", exclusion_criteria)
        return exclusion_criteria
    else:
        return data


async def main():
    max_pages = 16
    trials_per_page = 50
    total_trials_to_scrape = ((max_pages-1)*trials_per_page)
    collection, embedding_model = init()
    failed_list = []
    async with AsyncWebCrawler(verbose=False) as crawler:
        page_number = 1
        with tqdm(total=total_trials_to_scrape, desc='Clinical Trials Scraped: ') as pbar:
            while page_number<max_pages:
                # Get the currently recruiting Trial IDs
                trial_ids_set = await extract_nct_ids(crawler, 
                                                    trials_per_page,
                                                    page_number=page_number)

                for id in trial_ids_set:
                    # Check if ID exists already, if yes, skip:
                    if check_id_exists(collection, id): 
                        # print(id," exists", end='\r')
                        pbar.update(1)
                        continue
                    trial_page_details = await get_trial_details_by_id(crawler, id)
                    if trial_page_details is None: 
                        pbar.update(1)
                        failed_list.append(id)
                        continue
                    study_title = extract_title(trial_page_details["Study Overview"])
                    inclusion_criteria = extract_inclusion_criteria(trial_page_details["Participation Criteria"])
                    exclusion_criteria = extract_exclusion_criteria(trial_page_details["Participation Criteria"])
                    
                    data_to_embed = f'Inclusion Criteria: {inclusion_criteria}, Exclusion Criteria: {exclusion_criteria}'
                    embed_and_add_single_entry(collection, embedding_model, data_to_embed, id, study_title)
                    pbar.update(1)
                
                page_number+=1

    print(f"Finished scraping {total_trials_to_scrape} Clinical Trials. Added them to a local ChromaDB Vector Store")
    print(f"Here is a list trials that failed during scraping: ", failed_list)
    print(f"Total number of records in ChromaDB: ", collection.count())         

asyncio.run(main())