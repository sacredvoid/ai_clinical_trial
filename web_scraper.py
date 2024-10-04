import asyncio
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def extract_nct_ids(page_number=1):
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
    # js_code = """
    #         await new Promise(resolve => {
    #             window.onload = function() {
    #                 console.log('Page has fully loaded.');
    #                 resolve();
    #             };
    #         });
    #         """
    js_code = """
    (async () => {
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(resolve => setTimeout(resolve, 2000));  // Wait for 5 seconds
    })();
    """

    # Create the extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

    # Use the AsyncWebCrawler with the extraction strategy
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url=f"https://clinicaltrials.gov/search?viewType=Table&aggFilters=status:rec&limit=100&page={page_number}",
            extraction_strategy=extraction_strategy,
            js_code=js_code,
            bypass_cache=True
        )

        assert result.success, "Failed to crawl the page"
        # Parse the extracted content
        extracted_data = json.loads(result.extracted_content)
        # Parse JSON and go to the extracted page
        id_set = set(id['nct_id'] for id in extracted_data)
        print(id_set)
        trial_page_dict = {}
        for nct_id in id_set:
            # nct_id = row['nct_id']
            print("Processing: ",nct_id," #################")
            trial_details_per_id = await crawler.arun(
            url=f"https://clinicaltrials.gov/study/{nct_id}",
            bypass_cache=True
            )
            assert result.success, "Failed to crawl the page"
            print(trial_details_per_id.markdown)
            trial_page_dict[nct_id] = trial_details_per_id.markdown
            print("Finished adding to dict ################")
        


async def main():

    await extract_nct_ids()
    # page_number = 1
    # all_trials = []
    # while True:
    #     trial_ids = extract_nct_ids(page_number=page_number)
    #     if trial_ids:
    #         all_trials.append(trial_ids)
    #         page_number += 1
    #     else:
    #         break

asyncio.run(main())
