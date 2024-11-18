import os
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.docstore.document import Document as lnDoc
from typing import List

# Initialize embedding model
embedding_model = OllamaEmbeddings(model="nomic-embed-text")

def upload_json_to_vector_db(json_file_path: str):
    """
    Reads data from a JSON file and uploads it to a FAISS vector database.
    """
    index_name = "automation_framework_database"
    document_objs = []

    # Check if vector DB exists
    if os.path.exists(index_name):
        print("Database found. Loading existing index...")
        vector_db = FAISS.load_local(index_name, embeddings=embedding_model, allow_dangerous_deserialization=True)
        existing_titles = get_existing_titles(vector_db)
    else:
        print("Database not found. Creating a new index...")
        vector_db = None
        existing_titles = set()

    # Load data from JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Prepare new documents to add to the database
    for entry in data:
        unique_key = f"{entry['class_name']}_{entry['function_name']}"
        if unique_key in existing_titles:
            print(f"Skipping duplicate entry: {unique_key}")
            continue

        # Combine fields into document content
        document_content = (
            f"Class Name: {entry['class_name']}\n"
            f"Function Name: {entry['function_name']}\n"
            f"Description: {entry['description']}\n"
            f"Code Implementation:\n{entry['code']}\n"
            f"Input: {entry['input']}\n"
            f"Output: {entry['output']}"
        )
        metadata = {
            "class_name": entry["class_name"],
            "function_name": entry["function_name"],
        }
        document_objs.append(lnDoc(page_content=document_content, metadata=metadata))

    # Add new documents to the vector database
    if document_objs:
        if vector_db is None:
            vector_db = FAISS.from_documents(document_objs, embedding=embedding_model)
        else:
            vector_db.add_documents(document_objs)

        # Save updated database
        vector_db.save_local(index_name)
        print(f"Vector database saved as: {index_name}")
    else:
        print("No new entries to add to the database.")

def get_existing_titles(vector_db: FAISS) -> set:
    """
    Retrieves existing unique keys (class_name and function_name) from the database metadata.
    """
    existing_titles = set()
    for doc in vector_db.get_all_documents():
        metadata = doc.metadata
        unique_key = f"{metadata['class_name']}_{metadata['function_name']}"
        existing_titles.add(unique_key)
    return existing_titles

# Example usage
if __name__ == "__main__":
    json_file_path = "parsed_data.json"  # Replace with your JSON file path
    upload_json_to_vector_db(json_file_path)
