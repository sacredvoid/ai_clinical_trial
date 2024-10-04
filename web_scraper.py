import asyncio
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from collections import defaultdict
from tenacity import retry, stop_after_attempt, wait_exponential
import os

async def extract_nct_ids(crawler, trials_per_page=25, page_number=1):
    # Define the extraction schema
    # ctg-search-results-table p-table div#pn_id_2 table tr.ng-star-inserted 
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
        bypass_cache=True
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
    print("Processing: ",trial_id," #################")
    
    trial_details_per_id = await crawler.arun(
                            url=f"https://clinicaltrials.gov/study/{trial_id}",
                            extraction_strategy=extraction_strategy,
                            bypass_cache=True
                            )
    assert trial_details_per_id.success, "Failed to crawl the page"
    print(trial_details_per_id.extracted_content)
    # print(json.dumps(trial_details_per_id.extracted_data, indent=2))
    return json.loads(trial_details_per_id.extracted_content)[0]

def write_to_json(filename, data):
    save_dir = './clinical_trial_data'
    os.makedirs(save_dir, exist_ok=True)
    file_save_path = os.path.join(save_dir, filename)

    with open(file_save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Written file {file_save_path}")

async def main():
    max_pages = 15
    trials_per_page = 50
    async with AsyncWebCrawler(verbose=True) as crawler:
        page_number = 1
        
        while page_number<max_pages:
            trial_id_data_dict = defaultdict()
            # Get the currently recruiting Trial IDs
            trial_ids_set = await extract_nct_ids(crawler, 
                                                  trials_per_page,
                                                  page_number=page_number)

            for id in trial_ids_set:
                trial_page_details = await get_trial_details_by_id(crawler, id)
                trial_id_data_dict[id] = {}
                trial_id_data_dict[id]["Study Overview"] = trial_page_details["Study Overview"]
                trial_id_data_dict[id]["Participation Criteria"] = trial_page_details["Participation Criteria"]
            
            write_to_json(f'clinical_trial_data_page{page_number}.json', trial_id_data_dict)
            page_number+=1

asyncio.run(main())
