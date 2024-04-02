from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased_from_hf")
model = AutoModelForSequenceClassification.from_pretrained("allenai/scibert_scivocab_uncased_from_hf")

def expand_biomedical_query(query, top_k=5):
  """
  Expands a biomedical query using HyDE model.

  Args:
      query: The original biomedical query string.
      top_k: Number of top similar concepts to include in the expansion (default: 5).

  Returns:
      The expanded query string.
  """
  # Tokenize the query
  encoded_query = tokenizer(query, return_tensors="pt")

  # Get hidden layer outputs from the model
  with torch.no_grad():
    outputs = model(**encoded_query)
    last_hidden_state = outputs.last_hidden_state

  # Get word embeddings from the last hidden state
  word_embeddings = last_hidden_state.squeeze(0)

  # Calculate cosine similarity between query tokens and vocabulary
  query_embedding = word_embeddings[:, 0]  # Get embedding for the first token (CLS)
  vocab_embeddings = model.bert.embeddings.word_embeddings
  similarities = F.cosine_similarity(query_embedding.unsqueeze(0), vocab_embeddings).squeeze(0)

  # Get top K most similar words
  top_k_indices = torch.topk(similarities, top_k)[1]
  top_k_words = tokenizer.convert_ids_to_tokens(top_k_indices.tolist())

  # Expand the query with top K similar words (excluding CLS and SEP tokens)
  expanded_query = " ".join([word for word in [query] + top_k_words if word not in ["[CLS]", "[SEP]"]])

  return expanded_query

# Example usage
query = "protein-protein interaction network analysis"
expanded_query = expand_biomedical_query(query)
print(f"Original query: {query}")