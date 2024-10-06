import json
from summarize_apis.huggingface import summarize
from combine_patient_data import create_patient_profile, get_all_patient_ids
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from create_clinical_trial_embeddings import check_id_exists, get_or_create_collection, embed_and_add_single_entry

# Create instance of embedding model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# Create instance of ChromaDB client
client = PersistentClient("./chromadb_clinicaltrial")
# Get the collection object for our clinical trials collection
inclusion_collection = client.get_collection("inclusion_criteria")
exclusion_collection = client.get_collection("exclusion_criteria")
patient_collection = client.get_or_create_collection("patient_data")

def calculate_similarity(embedding1, embedding2):
    # embedding1 = np.atleast_2d(embedding1)
    # embedding2 = np.atleast_2d(embedding2)
    # if embedding1.ndim > 2:
    #     embedding1 = embedding1.reshape(1, -1)
    # if embedding2.ndim > 2:
    #     embedding2 = embedding2.reshape(1, -1)
    return cosine_similarity([embedding1], [embedding2])[0][0]

def find_matching_trials_per_patient(patient_id, top_k=100, score_threshold=0.1):
    """This function helps us find the matching clinical trials for a given patient.
    It takes in a patient ID, and top_k (default 100), to get 100 matching trials to given patient 
    based on vector search similarities.

    Args:
        patient_id (str): Patient ID
        top_k (int, optional): Get Top k matching elements. Defaults to 100.

    Returns:
        list: IDs of all the clinical trials
    """
    print("######### Find best trials for Patient: ", patient_id, " #######")
    # Check if patient profile already exists in vector form
    if check_id_exists(patient_collection, patient_id):
        print("Found existing patient details")
    else:
        # Create a patient profile - JSON - with all the important and relevant fields
        patient_profile_json = create_patient_profile(patient_id)
        
        try:
        # Send this to the LLM API, in this case HuggingFace API using Llama 3.2 3b Instruct
            summarized_patient_profile = summarize(patient_profile_json)
            print("SUMMARIZED PATIENT: ", summarized_patient_profile)
        except Exception as e:
            print("API Limit error: ", e, " for patient ID", patient_id)
            return
        
        # Create an embedding for this patient profile and upload to chromaDB
        embed_and_add_single_entry(patient_collection, model, summarized_patient_profile, patient_id)
    
    
    summarized_patient_profile = patient_collection.get(ids=patient_id, include=['embeddings', 'documents'])
    embedding_summarized_patient_profile = summarized_patient_profile['embeddings'][0]
    text_summarized_patient_profile = summarized_patient_profile['documents'][0]
    # Find closest matching trials to this patient vector from the trial vectors in the chromaDB
    inclusion_topk_matches = inclusion_collection.query(
        query_embeddings=embedding_summarized_patient_profile,
        include=['embeddings','metadatas'],
        n_results=top_k
    )
    # print(inclusion_topk_matches)
    
    trial_scores = []
    for i in range(top_k):
        trial_id = inclusion_topk_matches['ids'][0][i]
        inclusion_embedding = inclusion_topk_matches["embeddings"][0][i]

        exclusion_results = exclusion_collection.get(
            ids=trial_id,
            include=["embeddings"]
        )
        exclusion_embedding = exclusion_results['embeddings'][0]
        # print(len(embedding_summarized_patient_profile))
        # print(inclusion_embedding.shape)
        # print(exclusion_embedding.shape)
        similarity_inclusion = calculate_similarity(embedding_summarized_patient_profile, inclusion_embedding)
        similarity_exclusion = calculate_similarity(embedding_summarized_patient_profile, exclusion_embedding)
        
        score = 1 * similarity_inclusion - 1 * similarity_exclusion
        if score > score_threshold:
            trial_scores.append((trial_id, score))

    trial_scores.sort(key=lambda x: x[1], reverse=True)
    if len(trial_scores) > 15:
        n_candidates = 15
    elif len(trial_scores) < 10:
        n_candidates = len(trial_scores)  # Take all available scores if less than 10
    else:
        n_candidates = 10  # Default to 10 if between 10 and 15
    trial_scores = trial_scores[:n_candidates] # Taking only top n candidates from the top matching scores.
    # print(trial_scores)
    print("##############")
    print(f"Found: {len(trial_scores)} potentially compatible trials for patient: {patient_id}")
    print("Asking an expert LLM with these subsets to fetch the most relevant trials")
    print("###############")
    eligible_trials_json = {
        "patientId": patient_id,
        "eligibleTrials": []
    }
    for trial_ID, _ in trial_scores:
        matched_trial = medical_llm_filter(patient_id,
                            text_summarized_patient_profile, 
                           trial_ID)
        eligible_trials_json["eligibleTrials"].append(matched_trial)
    save_json_to_file(eligible_trials_json, f'patient_trials_matched/patient_{patient_id}.json')
    print("\n\n################################")
    # 

def medical_llm_filter(patient_id, patient_data, clinical_trial_id):
    inclusion_criterion = inclusion_collection.get(ids=clinical_trial_id)["documents"][0]
    exclusion_criterion_all = exclusion_collection.get(ids=clinical_trial_id)
    exclusion_criterion = exclusion_criterion_all["documents"][0]
    trial_name = exclusion_criterion_all["metadatas"][0]["study_title"]
    # print("INC CRI", inclusion_criterion)
    medical_prompt_template = f"""
    # Task
    Your job is to determine the eligibility score for the given patient based on the inclusion and exclusion criteria.

    # Patient
    Below is a clinical note describing the patient's current health status:
    ```
    {patient_data}
    ```

    # Inclusion Criterion
    The inclusion criterion being assessed is: "{inclusion_criterion}"

    # Exclusion Criterion
    The exclusion criterion being assessed is: "{exclusion_criterion}"

    # Assessment
    Analyze the patient's clinical note to assess eligibility for the trial. 
    - If any exclusion criteria are met, the score is automatically 0. 
    - If you're unsure whether any exclusion criteria are met based on the patient notes, make a note of that uncertainty.

    Your response should start with the probability score (0-1) indicating the patient's eligibility, followed by up to 4-5 sentences explaining the reasons for eligibility or ineligibility. 
    Be succinct and avoid summarizing the patient information.
    """


    medical_llm_verdict = summarize(medical_prompt_template, agent_prompt=False,max_tokens=500)
    print("- Medical Reasoning for Trial ID: ", clinical_trial_id)
    print(medical_llm_verdict)
    score = extract_score(medical_llm_verdict)
    if score >= 0.5:
        eligibility_reasons = medical_llm_verdict.splitlines()[1:]  # Skip the first line (the score)
        eligibility_criteria_met = []

        # You may need to further process eligibility_reasons to extract specific criteria
        for reason in eligibility_reasons:
            if reason.strip():  # Ensure it's not an empty line
                eligibility_criteria_met.append(reason.strip())

        # Add the trial details to the eligible trials
        trial_entry = {
            "trialId": clinical_trial_id,
            "trialName": trial_name,
            "eligibilityCriteriaMet": eligibility_criteria_met
        }
        return trial_entry

def save_json_to_file(json_data, filename):
    """
    Saves the JSON data to a file.

    Parameters:
    - json_data (dict): The JSON data to save.
    - filename (str): The name of the file to save the JSON data.
    """
    with open(filename, 'w') as json_file:
        json.dump(json_data, json_file, indent=2)
        print(f"JSON data saved to {filename}")


def extract_score(output):
    """
    Extracts the probability score from the output string.

    Parameters:
    - output (str): The output string containing the score and eligibility details.

    Returns:
    - float: The extracted probability score or None if not found.
    """
    try:
        # Split the output by lines and get the first line, which should contain the score
        score_line = output.splitlines()[0].strip()
        # Convert the score to a float
        score = float(score_line)
        return score
    except (IndexError, ValueError):
        # Return None if the score can't be extracted
        return None

def find_matching_trials_for_all():
    """
    Just a function to run the summarize and find matching trials on all patient IDs.
    Limited to 10 due to API Rate limits. 
    """
    patient_ids = get_all_patient_ids()
    API_LIMIT = 15
    for i in range(0, API_LIMIT): # Limiting due to API restrictions
        matching_trials = find_matching_trials_per_patient(patient_ids[i][0])
        

def main():
    find_matching_trials_for_all()

if __name__ == "__main__":
    main()