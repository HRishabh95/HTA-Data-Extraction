from transformers import pipeline
import pandas as pd
import torch
import spacy
import pandas as pd
import numpy as np
from collections import deque
summarizer = pipeline("summarization", model="Falconsai/medical_summarization")

content_df=pd.read_csv('sections_tmp.csv',sep='\t')

doc=content_df.iloc[0]['Clinical']

nlp = spacy.load("en_core_web_sm")  # Load spaCy model


def split_document(document, max_block_size=500):
  doc = nlp(document)
  sentences = [sent.text.strip() for sent in doc.sents]
  blocks = deque()
  current_block = []

  for sentence in sentences:
    if len(current_block) == 0 or len(" ".join(current_block).split()) + len(sentence.split()) <= max_block_size:
      current_block.append(sentence)
    else:
      blocks.append(" ".join(current_block))
      current_block = [sentence]

  if current_block:
    blocks.append(" ".join(current_block))

  return list(blocks)

blocks = split_document(content_df.iloc[0]['Clinical'])

doc_summary=summarizer(blocks, max_length=150, min_length=100, do_sample=False)

# Load the BART model and tokenizer
hf_name = 'pszemraj/led-large-book-summary'

summarizer = pipeline(
    "summarization",
    hf_name,
    device=0 if torch.cuda.is_available() else -1,
)

doc_summary_bart=summarizer(content_df.iloc[0]['Clinical'],max_length=3000, min_length=1000, do_sample=False)

