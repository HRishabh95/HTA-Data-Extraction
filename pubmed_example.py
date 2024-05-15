from Bio import Entrez
import xml.etree.ElementTree as ET
import csv
import json
Entrez.email="uhrishabh@gmail.com"
import spacy
import pandas as pd
import numpy as np
from collections import deque
from transformers import AutoTokenizer, AutoModel
import faiss
import torch

def reconstruct_words(entities):
    reconstructed_entities = {}
    current_word = ""
    current_type = None

    for entity in entities:
        if entity['entity_group'] not in reconstructed_entities:
            reconstructed_entities[entity['entity_group']] = []

        # Check if we're still on the same word/entity type
        if entity['entity_group'] == current_type:
            # If the word part starts with ##, it's a continuation of the current word
            if entity['word'].startswith('##'):
                current_word += entity['word'].replace('##', '')
            else:
                # If not, it's a new word of the same type, so save the current word and start a new one
                reconstructed_entities[current_type].append(current_word)
                current_word = entity['word']
        else:
            # We're on a new type, so save the current word (if it exists) and start a new one
            if current_word:
                reconstructed_entities[current_type].append(current_word)
            current_word = entity['word']
            current_type = entity['entity_group']

    # Don't forget to add the last word
    if current_word:
        reconstructed_entities[current_type].append(current_word)

    return reconstructed_entities


def combine_medication_with_disorder(entities):
    reconstructed_entities = reconstruct_words(entities)

    # Assuming there is one-to-one mapping for simplicity
    medication = ' '.join(reconstructed_entities.get('Medication', []))
    disease_or_disorder = ' '.join(reconstructed_entities.get('Disease_disorder', []))

    return {'medication': medication, 'disease_or_disorder': disease_or_disorder}

def search_articles(query):
    handle = Entrez.esearch(db="pmc", term=query + " AND \"open access\"[filter]", retmax=10)
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]


def fetch_details(id_list):
    ids = ",".join(id_list)
    handle = Entrez.efetch(db="pmc", id=ids, retmode="xml")
    articles_xml = handle.read()  # Directly read the raw XML data
    handle.close()
    return articles_xml



def extract_information(article_xml):
    articles_info = []

    # Parse the XML using ElementTree
    root = ET.fromstring(article_xml)
    articles = root.findall('.//article')

    for article in articles:
        article_info = {"title": None, "abstract": None, "sections": []}

        # Extracting the title
        article_title = article.find('.//article-title')
        if article_title is not None:
            article_info["title"] = " ".join(article_title.itertext()).replace("  "," ")

        # Extracting the abstract
        abstract = article.find('.//abstract')
        if abstract is not None:
            article_info["abstract"] = " ".join(abstract.itertext()).replace("  "," ")

        # Extracting sections
        sections = article.findall('.//sec')
        for sec in sections:
            section_title = sec.find('.//title')
            title_text = section_title.text if section_title is not None else "No Title"
            section_text = " ".join(sec.itertext()).replace("  "," ")
            article_info["sections"].append({"title": title_text, "text": section_text})

        articles_info.append(article_info)

    return articles_info

def save_as_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification

tokenizer = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
model = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")

pipe = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple") # pass device=0 if using gpu

query_unclean = "Avelumab with axitinib for untreated advanced renal cell carcinoma"

ner_disease=pipe(query_unclean)
combined = combine_medication_with_disorder(ner_disease)

query=f'''{combined['medication']}[All fields] AND {combined['disease_or_disorder']}[All fields]'''
article_ids = search_articles(query)
articles_xml = fetch_details(article_ids)
articles_info = extract_information(articles_xml)



from langchain.text_splitter import SpacyTextSplitter
text_splitter = SpacyTextSplitter(chunk_size=400)



model_name = 'ncbi/MedCPT-Query-Encoder'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def create_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    # Use the mean of the last hidden states as the document embedding
    embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    return embeddings


index_abs = faiss.IndexFlatL2(768)  # Assuming 768 is the embedding size
mapping=[]


# Function to add block to index and mapping
def add_block_to_index(index, mapping, document_id, block_number, embedding,block):
    index.add(embedding.reshape(1, -1))  # Add embedding to FAISS index
    mapping.append((document_id, block_number,block))  # Add document ID and block number to mapping

for index, document in enumerate(articles_info[:3]):
    for column_name, index_obj, mapping in [('Abs', index_abs, mapping)]:
        column_text = document['abstract']
        if pd.notnull(column_text):
            blocks = text_splitter.split_text(column_text)
            for block_number, block in enumerate(blocks):
                embedding = create_embeddings(block)[0]  # Convert block to embedding
                add_block_to_index(index_obj, mapping, article_ids[index], block_number, embedding,block)



def search_vector_db_with_auto_column(user_query):
  query_embedding = create_embeddings(user_query)[0].reshape(1, -1)

  D, I = index_abs.search(query_embedding, k=5)
  mappings = mapping

  search_results = [(mappings[i][0], mappings[i][2]) for i in I[0]]  # Assuming I is a 2D array with shape (1, k)
  return search_results

results = search_vector_db_with_auto_column(f'''{combined['medication']} {combined['disease_or_disorder']}''')
