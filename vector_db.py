import spacy
import pandas as pd
import numpy as np
from collections import deque
from transformers import AutoTokenizer, AutoModel
import faiss
import torch


nlp = spacy.load("en_core_web_sm")  # Load spaCy model

def split_document(document, max_block_size=510):
  doc = nlp(document)
  sentences = [sent.text.strip() for sent in doc.sents]
  blocks = deque()
  current_block = []

  for sentence in sentences:
    if len(current_block) == 0 or len(" ".join(current_block)) + len(sentence) <= max_block_size:
      current_block.append(sentence)
    else:
      blocks.append(" ".join(current_block))
      current_block = [sentence]

  if current_block:
    blocks.append(" ".join(current_block))

  return list(blocks)

documents=pd.read_csv('sections_tmp.csv',sep='\t')

model_name = 'ncbi/MedCPT-Article-Encoder'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Function to create embeddings for a block of text
def create_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    # Use the mean of the last hidden states as the document embedding
    embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    return embeddings

# Load documents
documents = pd.read_csv('sections_tmp.csv', sep='\t')

# Initialize FAISS index for each column
index_intro = faiss.IndexFlatL2(768)  # Assuming 768 is the embedding size
index_clinical = faiss.IndexFlatL2(768)
index_cost = faiss.IndexFlatL2(768)

# Initialize mappings
mapping_intro = []
mapping_clinical = []
mapping_cost = []

# Function to add block to index and mapping
def add_block_to_index(index, mapping, document_id, block_number, embedding,block):
    index.add(embedding.reshape(1, -1))  # Add embedding to FAISS index
    mapping.append((document_id, block_number,block))  # Add document ID and block number to mapping

for index, document in documents.head(2).iterrows():
    for column_name, index_obj, mapping in [('Intro', index_intro, mapping_intro),
                                            ('Clinical', index_clinical, mapping_clinical),
                                            ('Cost', index_cost, mapping_cost)]:
        column_text = document[column_name]
        if pd.notnull(column_text):
            blocks = split_document(column_text)
            for block_number, block in enumerate(blocks):
                embedding = create_embeddings(block)[0]  # Convert block to embedding
                add_block_to_index(index_obj, mapping, document['ID'], block_number, embedding,block)

# Function to search in vector DB
column_descriptions = {
  'Intro': "This section provides an overview and background information.",
  'Clinical': "This section discusses the clinical outcomes and effectiveness of treatments.",
  'Cost': "This section analyzes the cost-effectiveness of different medical interventions."
}

# Create embeddings for column descriptions
column_embeddings = {column: create_embeddings(description)[0] for column, description in column_descriptions.items()}


# Updated search function that chooses the column based on similarity
def search_vector_db_with_auto_column(query):
  query_embedding = create_embeddings(query)[0].reshape(1, -1)

  # Compute similarity with column descriptions
  similarities = {}
  for column, embedding in column_embeddings.items():
    # Compute cosine similarity, for simplicity we use dot product assuming embeddings are normalized
    similarity = np.dot(query_embedding, embedding.reshape(-1, 1)) / (
              np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
    similarities[column] = similarity

  # Choose the column with the highest similarity
  chosen_column = max(similarities, key=similarities.get)

  # Based on the chosen column, select the index for searching
  if chosen_column == 'Intro':
    D, I = index_intro.search(query_embedding, k=5)
    mappings=mapping_intro
  elif chosen_column == 'Clinical':
    D, I = index_clinical.search(query_embedding, k=5)
    mappings=mapping_clinical
  elif chosen_column == 'Cost':
    D, I = index_cost.search(query_embedding, k=5)
    mappings=mapping_cost

  search_results = [(mappings[i][0], mappings[i][2]) for i in I[0]]  # Assuming I is a 2D array with shape (1, k)
  return chosen_column, search_results


results = search_vector_db_with_auto_column("Cost Effectiveness of the Dapagliflozin")
print(results)