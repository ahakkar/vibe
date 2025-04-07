import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime, timezone
import uuid

EMBED_MODEL = "TurkuNLP/sbert-cased-finnish-paraphrase"
path = "./chroma_db"

class Chroma:
    
    def __init__(self):
        # Load Finnish embedding model
        self.embedding_model = SentenceTransformer(EMBED_MODEL)

        # Set up ChromaDB (persistent storage)
        self.chroma_client = chromadb.PersistentClient(path)
        
        
        # self.chroma_client.delete_collection(name="voice_data")
        # Uncomment line above for clearing the persistent storage
        
        self.collection = self.chroma_client.get_or_create_collection(name="voice_data")

    def save_to_db(self, entry):

        #Create embedding for the entry
        embedding = self.embedding_model.encode(entry)

        #Create unique id
        id = str(uuid.uuid4())

        timestamp = datetime.now(timezone.utc).isoformat()
        metadata = {
            "timestamp": timestamp
        }

        self.collection.add(
            ids = [id],
            embeddings = [embedding.tolist()],
            metadatas = [metadata],
            documents = [entry]
        )

        print("Context saved:" + entry)
        print(self.collection)

    def retrieve_similar_entries(self, query, n=1):

        # Generate the embedding for the query text
        query_embedding = self.embedding_model.encode(query)

        # Query the ChromaDB collection for the most similar documents
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],  # Use query embedding for similarity search
            n_results = n  
        )

        return results['documents']  