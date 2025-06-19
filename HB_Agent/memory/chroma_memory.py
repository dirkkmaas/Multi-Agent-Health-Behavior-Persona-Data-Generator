import json
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from config import OPENAI_API_KEY


class ChromaMemory:
    """Vector database for semantic memory and episodic memory. Uses similarity search to find the most relevant messages to a quiry"""
    def __init__(self, db_path: str = "/chroma_db/Data"):
        """Initialize ChromaDB with LangChain and Ollama embeddings."""
        self.db_path = db_path
        self.embedding_function = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="text-embedding-3-small",) # specify openai model

    def _get_vectorstore(self, collection_name: str):
        """Returns a Chroma vectorstore for the given collection."""
        return Chroma(persist_directory=self.db_path, embedding_function=self.embedding_function, collection_name=collection_name)

    def add_entry(self, entry: dict, collection_name: str):
        """Stores a message as one entry in ChromaDB."""
        entry_json = json.dumps(entry)  # Convert dictionary to JSON string
        document = Document(page_content=entry_json)  # Store as a single document
        vectorstore = self._get_vectorstore(collection_name)
        vectorstore.add_documents([document])
        print(f" 1 structured entry stored in collection '{collection_name}' successfully!") # print confirmation

    def search(self, query: str, collection_name: str, top_k: int = 3):
        """Performs a similarity search and returns the top K most relevant messages, standard 3 ."""
        vectorstore = self._get_vectorstore(collection_name)
        results = vectorstore.similarity_search(query, k=top_k)
        
        if results:
            return [json.loads(doc.page_content) for doc in results]  # Convert JSON string back to dictionary
        else:
            return None
            
    def print_all_entries(self, collection_name: str):
        """Retrieves and prints all entries from a given collection.
        Not implemented in streamlit but might be useful for future use"""
        vectorstore = self._get_vectorstore(collection_name)
        results = vectorstore.similarity_search("", k=1000)  #k is high for number of entries

        if not results:
            print(f"No entries found in collection '{collection_name}'.")
            return
        
        print(f"Entries in collection '{collection_name}':\n")
        
        for i, doc in enumerate(results):
            print(f"Entry {i+1}:")
            try:
                parsed_json = json.loads(doc.page_content)
                print(json.dumps(parsed_json, indent=4))  
            except json.JSONDecodeError:
                print(f"Raw Content (Not JSON): {doc.page_content}")
            print("-" * 50)  # Separator for readability

    def clear_collection(self, collection_name: str):
        """Deletes all entries from a collection or the collection itself if supported 
        currently not in streamlit, but might be usefull in future."""
        vectorstore = self._get_vectorstore(collection_name)
        if hasattr(vectorstore, "delete_collection"):
            vectorstore.delete_collection()  # Deletes everything
            print(f"Collection '{collection_name}' deleted.")
        else:
            print(f"Collection not deleted.")

