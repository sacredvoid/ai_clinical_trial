from summarize_apis.openrouter import summarize
from combine_patient_data import create_patient_profile, get_all_patient_ids
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

# Create instance of embedding model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# Create instance of ChromaDB client
client = PersistentClient("./chromadb_clinicaltrial")
# Get the collection object for our clinical trials collection
collection = client.get_collection("clinical_trials")

def find_matching_trials_per_patient(patient_id, top_k=5):
    """This function helps us find the matching clinical trials for a given patient.
    It takes in a patient ID, and top_k (default 5), to get 5 matching trials to given patient 
    based on vector search similarities.

    Args:
        patient_id (str): Patient ID
        top_k (int, optional): Get Top k matching elements. Defaults to 5.

    Returns:
        _type_: _description_
    """
    # Create a patient profile - JSON - with all the important and relevant fields
    patient_profile_json = create_patient_profile(patient_id)
    
    # Send this to the LLM API, in this case OpenRouter API using Llama 3.2 3b Instruct
    summarized_patient_profile = summarize(patient_profile_json)
    # print("SUMMARIZED PATIENT: ", summarized_patient_profile)
    
    # Create an embedding for this patient profile
    embedding_summarized_patient_profile = model.encode(summarized_patient_profile, convert_to_tensor=False).tolist()
    # print("EMBEDDED: ######",embedding_summarized_patient_profile)
    
    # Find closest matching trials to this patient vector from the trial vectors in the chromaDB
    results = collection.query(
        query_embeddings=embedding_summarized_patient_profile,
        n_results=top_k
    )
    
    # Process the results
    closest_embeddings = results['embeddings']  # Access the embeddings
    closest_ids = results['ids']  # Access the IDs of the closest items
    closest_distances = results['distances']  # Access the distances, if needed
    print(f"Closest IDs for patient {patient_id}: {closest_ids}")
    print(f"Distances: {closest_distances}")
    return results['ids']

    
def find_matching_trials_for_all():
    """
    Just a function to run the summarize and find matching trials on all patient IDs.
    Limited to 10 due to API Rate limits. 
    """
    patient_ids = get_all_patient_ids()
    API_LIMIT = 10
    for i in range(0, API_LIMIT): # Limiting due to API restrictions
        matching_trials = find_matching_trials_per_patient(patient_ids[i][0])
        

def main():
    find_matching_trials_for_all()

if __name__ == "__main__":
    main()