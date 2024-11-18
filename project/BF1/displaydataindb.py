from langchain_community.vectorstores import FAISS
import numpy as np
from sentence_transformers import SentenceTransformer

index_name = 'faiss_index.index'
model_name = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(model_name)
vector_db = FAISS.load_local(index_name, embeddings=embedding_model, allow_dangerous_deserialization=True)
existing_docs = vector_db.similarity_search("", k=1000)  # Get all documents)
print(existing_docs)