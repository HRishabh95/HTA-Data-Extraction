import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import defaultdict
from heapq import nlargest

nltk.download('punkt')
nltk.download('stopwords')


def summarize_text(text, n_sentences=5):
    nltk.download('punkt')
    nltk.download('stopwords')

    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    # Tokenize the text into words and calculate word frequencies, ignoring stopwords
    stop_words = set(stopwords.words("english"))
    word_frequencies = defaultdict(int)

    for word in word_tokenize(text.lower()):
        if word not in stop_words:
            word_frequencies[word] += 1

    # Calculate the maximum word frequency
    max_frequency = max(word_frequencies.values())

    # Normalize frequencies and score sentences
    for word in word_frequencies:
        word_frequencies[word] = (word_frequencies[word] / max_frequency)
    sentence_scores = defaultdict(int)

    for sent in sentences:
        for word in word_tokenize(sent.lower()):
            if word in word_frequencies:
                sentence_scores[sent] += word_frequencies[word]

    # Select the top n sentences with the highest scores
    summary_sentences = nlargest(n_sentences, sentence_scores, key=sentence_scores.get)

    # Join the selected sentences
    summary = ' '.join(summary_sentences)
    return summary


# Example usage
text = """Your very long text here..."""  # Replace this with your actual text
summary = summarize_text(sections_content[1][1], n_sentences=100)  # Adjust n_sentences as needed
print(summary)