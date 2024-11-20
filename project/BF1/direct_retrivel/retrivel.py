import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings  # Or use OpenAIEmbeddings
import streamlit as st

# Function to retrieve relevant user story
def get_relevant_user_story(vector_store, txt):
    existing_docs = vector_store.similarity_search(txt, k=5)
    st.success("Relevant document retrieved successfully!")
    st.write(existing_docs)

# Streamlit UI for input and button
st.title("User Story Retrieval")

user_story = st.text_area("Enter User Story", placeholder="Describe your user story here...")

if st.button("Get the User Story"):
    # Path to the database folder
    database_folder = "automation_framework_database"

    try:
        st.info("Loading the vector database...")
        embeddings = OllamaEmbeddings(model="nomic-embed-text")  # Initialize the embedding model
        vector_db = FAISS.load_local(database_folder, embeddings=embeddings, allow_dangerous_deserialization=True)
        get_relevant_user_story(vector_db, user_story)
    except Exception as e:
        st.error(f"Error while loading vector database or retrieving user story: {str(e)}")
