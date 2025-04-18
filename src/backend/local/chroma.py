import os
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime, timezone
import uuid
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

EMBED_MODEL = "TurkuNLP/sbert-cased-finnish-paraphrase"
path = "./chroma_db"


class Chroma:

    def __init__(self, project_root):
        """
        Initialize the RAG service.
        The function sets up the embedding model and the ChromaDB client.
        It also creates a collection in the database to store the entries.
        """
        try:
            embed_filepath = (
                str(project_root)
                + "/"
                + os.getenv("MODEL_FOLDER")
                + "/"
                + os.getenv("EMBEDDING_MODEL")
            )

            self.embedding_model = SentenceTransformer(embed_filepath)

        except Exception as e:
            print(f"Error loading model: {e}")
            raise

        self.chroma_client = chromadb.PersistentClient(path)

        # self.chroma_client.delete_collection(name="voice_data")
        # Uncomment line above for clearing the persistent storage

        self.collection = self.chroma_client.get_or_create_collection(name="voice_data")

    def save_to_db(self, entry):
        """
        Save the entry to the database. The function encodes the entry using the embedding model,
        generates a unique ID, and adds the entry to the ChromaDB collection.
        The entry is stored with its embedding and metadata (timestamp).
        :param str entry: The entry to be saved in the database.
        """

        embedding = self.embedding_model.encode(entry)

        id = str(uuid.uuid4())

        timestamp = datetime.now(timezone.utc).isoformat()
        metadata = {"timestamp": timestamp}

        self.collection.add(
            ids=[id],
            embeddings=[embedding.tolist()],
            metadatas=[metadata],
            documents=[entry],
        )

    def retrieve_similar_entries(self, query, n=1, similarity_threshold=0.65):
        """
        Retrieve the most similar entries from the database based on the query.
        The function uses cosine similarity to find the closest match.
        If the similarity is above the threshold, it returns the most similar entry.
        Otherwise, it returns an empty string.

        :param str quert: The query string to search for in the database.
        :param int n: The number of similar entries to retrieve.
        :param float similarity_threshold: The threshold for cosine similarity to consider a match.
        :return str: The most similar entry from the database or an empty string if no match is found.
        """

        query_embedding = self.embedding_model.encode(query)

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            include=["embeddings", "documents"],
            n_results=n,
        )

        if not results["documents"][0]:
            return ""

        top_document = results["documents"][0][0]
        top_embedding = np.array(results["embeddings"][0][0])

        similarity = cosine_similarity([query_embedding], [top_embedding])[0][0]

        print("\nTop context smilarity:", similarity)

        if similarity >= similarity_threshold:
            return top_document
        else:
            return ""
