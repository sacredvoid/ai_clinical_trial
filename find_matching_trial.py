from summarize_apis.openrouter import summarize
from combine_patient_data import create_patient_profile, get_all_patient_ids
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
client = PersistentClient("./chromadb_clinicaltrial")
collection = client.get_collection("clinical_trials")

def find_matching_trials_per_patient(patient_id, top_k=5):
    patient_profile_json = create_patient_profile(patient_id)
    summarized_patient_profile = summarize(patient_profile_json)
    print("SUMMARIZED PATIENT: ", summarized_patient_profile)
    embedding_summarized_patient_profile = model.encode(summarized_patient_profile, convert_to_tensor=False).tolist()
    # print("EMBEDDED: ######",embedding_summarized_patient_profile)
    
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

    # You can now work with the closest embeddings as needed
    
def find_matching_trials_for_all():
    patient_ids = get_all_patient_ids()
    API_LIMIT = 10
    for i in range(0, API_LIMIT): # Limiting due to API restrictions
        matching_trials = find_matching_trials_per_patient(patient_ids[i][0])
        

def main():
    find_matching_trials_for_all()

if __name__ == "__main__":
    main()