import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

def get_or_create_collection(client, collection_name):
    """Helps to create a ChromaDB collection if it doesn't already exist

    Args:
        client (ChromaDB client): a chromaDB client
        collection_name (str): Name of your ChromaDB collection

    Returns:
        chromadb.collection: the collection object
    """
    # Check if the collection already exists
    existing_collections = client.list_collections()
    for collection in existing_collections:
        if collection.name == collection_name:
            return client.get_collection(collection_name)
    
    # If it doesn't exist, create the collection
    return client.create_collection(collection_name)

def init():
    """Initialization of ChromaDB client, collection and embedding model

    Returns:
        tuple: (collection, collection, model)
    """
# Initialize ChromaDB client and create a collection
    client = chromadb.PersistentClient(path="./chromadb_clinicaltrial")
    # Separate collections for inclusion and exclusion criteria
    inclusion_collection = get_or_create_collection(client, "inclusion_criteria")
    exclusion_collection = get_or_create_collection(client, "exclusion_criteria")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return inclusion_collection, exclusion_collection, model

def embed_and_add_single_entry(collection, model, data, id, study_title=None):
    """As the name suggests, Embed input data, add to ChromaDB collection

    Args:
        collection (chromadb.collection): ChromaDB collection object
        model (embedding model): The embedding model object
        data (str): The data to embed and store in chromadb
        id (str): ID of the data
        study_title (str, optional): Title study, in this case clinical trial

    Returns:
        None
    """
# Sample data (embedding and metadata)
    embedding = model.encode(data, convert_to_tensor=False).tolist()
    if study_title is not None:
        metadata = {"trial_id": id, "study_title": study_title}
    else:
        metadata = {"patient_id": id}

    collection.upsert(
        embeddings=[embedding],
        documents=[data],
        metadatas=[metadata],
        ids=[id]
    )
    # if 'ids' in response:
    #     print(f"Successfully added trial ID: {id} with embedding.")
    # else:
    #     print(f"Failed to add trial ID: {id}. Response: {response}")

def check_id_exists(collection, id_to_check):
    """Checks if an item already exists given it's ID

    Args:
        collection (chromadb.collection): collection object
        id_to_check (str): the ID to check if it exists

    Returns:
       bool: True/False depending on whether ID exists
    """
    result = collection.get(ids=[id_to_check])
    return len(result['ids']) > 0

def embed_and_add_multiple_entry(data):
    """Function to add multiple entries, requires data to be in a dict, key as ID and value containing data
    of the clinical trial

    Args:
        data (dict): Dictionary of data
    
    Returns:
        None
    """
    collection, embedding_model = init()
    if isinstance(data, dict):
        for key, value in tqdm(data.items(), desc="Processing Trials: "):
            id = key
            study_title = value['Study Title']
            inclusion_criteria = value['Inclusion Criteria']
            exclusion_criteria = value['Exclusion Criteria']
            data_to_embed = f'Inclusion Criteria: {inclusion_criteria}, Exclusion Criteria: {exclusion_criteria}'
            embed_and_add_single_entry(collection, embedding_model, data_to_embed, id, study_title)