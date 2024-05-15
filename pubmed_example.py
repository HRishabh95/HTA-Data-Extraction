from Bio import Entrez
import xml.etree.ElementTree as ET
import json
import pandas as pd
from transformers import AutoTokenizer, AutoModel, pipeline, AutoModelForTokenClassification
import faiss
from langchain.text_splitter import SpacyTextSplitter

# Function to reconstruct words from entities
def reconstruct_words(entities):
    reconstructed_entities = {}
    current_word = ""
    current_type = None

    for entity in entities:
        if entity['entity_group'] not in reconstructed_entities:
            reconstructed_entities[entity['entity_group']] = []

        if entity['entity_group'] == current_type:
            if entity['word'].startswith('##'):
                current_word += entity['word'].replace('##', '')
            else:
                reconstructed_entities[current_type].append(current_word)
                current_word = entity['word']
        else:
            if current_word:
                reconstructed_entities[current_type].append(current_word)
            current_word = entity['word']
            current_type = entity['entity_group']

    if current_word:
        reconstructed_entities[current_type].append(current_word)

    return reconstructed_entities

# Function to combine medication with disorder
def combine_medication_with_disorder(entities):
    reconstructed_entities = reconstruct_words(entities)
    medication = ' '.join(reconstructed_entities.get('Medication', []))
    disease_or_disorder = ' '.join(reconstructed_entities.get('Disease_disorder', []))
    return {'medication': medication, 'disease_or_disorder': disease_or_disorder}

# Function to search articles
def search_articles(query):
    handle = Entrez.esearch(db="pmc", term=query + " AND \"open access\"[filter]", retmax=10)
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]

# Function to fetch article details
def fetch_details(id_list):
    ids = ",".join(id_list)
    handle = Entrez.efetch(db="pmc", id=ids, retmode="xml")
    articles_xml = handle.read()
    handle.close()
    return articles_xml

# Function to extract information from articles
def extract_information(article_xml):
    articles_info = []
    root = ET.fromstring(article_xml)
    articles = root.findall('.//article')

    for article in articles:
        article_info = {"title": None, "abstract": None, "sections": []}
        article_title = article.find('.//article-title')
        if article_title is not None:
            article_info["title"] = " ".join(article_title.itertext()).replace("  "," ")
        abstract = article.find('.//abstract')
        if abstract is not None:
            article_info["abstract"] = " ".join(abstract.itertext()).replace("  "," ")
        sections = article.findall('.//sec')
        for sec in sections:
            section_title = sec.find('.//title')
            title_text = section_title.text if section_title is not None else "No Title"
            section_text = " ".join(sec.itertext()).replace("  "," ")
            article_info["sections"].append({"title": title_text, "text": section_text})
        articles_info.append(article_info)
    return articles_info

# Function to save data as JSON
def save_as_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Function to create embeddings
def create_embeddings(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    return embeddings

# Function to add block to index and mapping
def add_block_to_index(index, mapping, document_id, block_number, embedding, block):
    index.add(embedding.reshape(1, -1))
    mapping.append((document_id, block_number, block))

# Function to search vector DB with auto column
def search_vector_db_with_auto_column(user_query, index, mapping, tokenizer, model):
    query_embedding = create_embeddings(user_query, tokenizer, model)[0].reshape(1, -1)
    D, I = index.search(query_embedding, k=5)
    search_results = [(mapping[i][0], mapping[i][2]) for i in I[0]]
    return search_results

# Main function
def main():
    Entrez.email = input("Enter your email for PubmedAPI (any email): ")

    tokenizer_ner = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
    model_ner = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")
    pipe = pipeline("ner", model=model_ner, tokenizer=tokenizer_ner, aggregation_strategy="simple")

    user_query = input("Enter your query: ")
    ner_disease = pipe(user_query)
    combined = combine_medication_with_disorder(ner_disease)

    query = f'''{combined['medication']}[All fields] AND {combined['disease_or_disorder']}[All fields]'''
    article_ids = search_articles(query)
    articles_xml = fetch_details(article_ids)
    articles_info = extract_information(articles_xml)

    text_splitter = SpacyTextSplitter(chunk_size=400)

    model_name = 'ncbi/MedCPT-Query-Encoder'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    index_abs = faiss.IndexFlatL2(768)
    mapping = []

    for idx, document in enumerate(articles_info[:3]):
        column_text = document['abstract']
        if pd.notnull(column_text):
            blocks = text_splitter.split_text(column_text)
            for block_number, block in enumerate(blocks):
                embedding = create_embeddings(block, tokenizer, model)[0]
                add_block_to_index(index_abs, mapping, article_ids[idx], block_number, embedding, block)

    results = search_vector_db_with_auto_column(f'''{combined['medication']} {combined['disease_or_disorder']}''', index_abs, mapping, tokenizer, model)

    print("Search results:")
    for result in results:
        print(f"Article ID: {result[0]}, Text: {result[1]}")

if __name__ == "__main__":
    main()
