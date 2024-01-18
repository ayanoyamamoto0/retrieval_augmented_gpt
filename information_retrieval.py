# Import required libraries
import os
import spacy
from nltk.metrics import jaccard_distance
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Define the standard stop words
stop_words = nlp.Defaults.stop_words

# Create a list of custom stop words
custom_stop_words = ['course', 'year', 'level', 'student', 'entry', 'apply', 'study', 'minimum',
                     'english', 'work', 'award', 'module', 'time', 'application', 'tu', 'eu', 
                     'requirements', 'school', 'advanced', 'contact', 'programme', 'website', 'applicant',
                      'qqi', 'ects', 'credit']

# ----- Create a function to preprocess text -----

# Function to preprocess text
def preprocess (text):
    # Create an empty list to save processed text
    preprocessed_doc = []
    # Process the input text and create an NLP doc object
    doc = nlp(text)
    # Loop through teach token in doc
    for token in doc:
        # Remove special characters, standard stop words, and custom stop words
        if token.lemma_.isalpha() and token.lemma_.lower() not in stop_words and token.lemma_.lower() not in custom_stop_words:
            # Lemmatize and append to 'preprocessed_doc' list
            preprocessed_doc.append(token.lemma_.lower())
    # Return the list as the outcome        
    return preprocessed_doc


# ----- File loading and preprocessing -----

# Set a folder path
folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'corpus')

# Create a list of file names
course_names_with_ext = os.listdir(folder_path)

# Remove '.txt' from and save the course names only
course_names_raw = [os.path.splitext(file_name)[0] for file_name in course_names_with_ext]

# Clean unwanted characters
course_names = [name.replace('\xa0', ' ') for name in course_names_raw]


# Create an empty list to store the raw corpus
corpus_raw = []

# Loop through the files in the 'corpus' folder and store them in 'corpus_raw' list
# Loop through each file in the folder
for file in os.listdir(folder_path):
    # Open file and read the contents
    with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as file:
        # Append to 'corpus_raw' list
        corpus_raw.append(file.read())

# Create an empty list to store the processed corpus
corpus_processed = []

# Loop through the 'corpus_raw' list and process the text
# Loop through each document in 'corpus_raw' list
for doc in corpus_raw:
    # Preprocess the doc object
    preprocessed_doc = preprocess(doc)
    # Append to 'corpus_preprocessed' list
    corpus_processed.append(' '.join(preprocessed_doc))


# ----- Encode the corpus using bag of words -----
# Create a set of tokens for each document in 'corpus_processed'
corpus_bow = [set(doc.split())for doc in corpus_processed]


# ----- Encode the corpus using TF-IDF -----
# Create an instance of TfidfVectorizer class
vectorizer = TfidfVectorizer()

# Transform the 'corpus_processed' into TF-IDF representation
corpus_tfidf = vectorizer.fit_transform(corpus_processed)


# ----- Encode the corpus using sentence encoding -----
# creates an instance of the SentenceTransformer class with a distilled version of the BERT base model
model = SentenceTransformer('distilbert-base-uncased')

# Encode each sentence in the 'corpus_raw'
corpus_bert = [model.encode(doc) for doc in corpus_raw]


# ----- Function to compare bags of words using Jaccard distance -----

def bow_jaccard(input):

    # Tokenize the input
    input_tokens = set(preprocess(input))

    # Calculate the Jaccard distance between the user input and each document in the corpus
    # Create an empty list to store jaccard distances
    distances = []
    # Loop through each document in the encoded corpus
    for doc in corpus_bow:
        # Calculate the Jaccard distance between the input and the document
        distance = jaccard_distance(input_tokens, doc)
        # Append the Jaccard distance to 'distance' list
        distances.append(distance)

    # Sort the distances and get the indices of the top 5 most similar documents
    top_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:5]

    # Return the indices of the top 5 most similar documents
    return top_indices


# ----- Function to compare TF-IDF encodings with cosine similarity -----

def tfidf_cosine(input):

    # Preprocess the input
    input_processed = preprocess(input)

    # Transform the processed input into TF-IDF representation
    input_vector = vectorizer.transform(input_processed)

    # Calculate the cosine similarity between the input and the documents in the corpus
    similarities = cosine_similarity(input_vector, corpus_tfidf)

    # Get the indices of the top 5 most similar files
    top_similarities = similarities.argsort()[0][::-1][:5]

    # Return the indices of the top 5 most similar files
    return top_similarities


# ----- Function to compare distilbert encodings with Euclidean distance -----

def bert_euclidean(input):

    # Encode the input
    input_embedding = model.encode(input)

    # Calculate the Euclidean distance between the input and the documents in the corpus
    distances = [np.linalg.norm(input_embedding - embedding) for embedding in corpus_bert]

    # Get the indices of the top 5 most similar files
    top_indices = np.argsort(distances)[:5]

    # Return the indices of the top 5 most similar documents
    return top_indices


# ----- Function to return course names specified by indices -----

def name_lookup(indices):

    # Match the indices with course names
    file_names = [course_names[i] for i in indices]

    # Return the course names
    return file_names


# ----- Test with 10 sample query sentences -----

# Create a list of lists for test queries and their expected answers (course names)
test_queries = [['I’m interested in the ethics of Artificial Intelligence.', 'Master of Science in Computing in Human Centered Artificial Intelligence'], 
                ['I already work in real estate and I want to skill up.', 'Higher Certificate in Business in Real Estate (Valuation, Sale and Management)'], 
                ['I want to do an internship related to cyber security.', 'Bachelor of Science (Honours) in Computing in Digital Forensics and Cyber Security'],
                ['My dream is to perform on stage in an orchestra.', 'Master of Music (Performance)'],
                ['I became interested in immunology after the COVID-19.', 'Bachelor of Science (Honours) in Medical Science'],
                ['I am concerned about environmental issues.', 'Master of Science in Energy Management'],
                ['I’m an international student and need support with English.', 'International Bridging Programme for Undergraduate Studies'],
                ['I’m not sure what I want to do now, I’m looking for a flexible course.', 'Bachelor of Business (allowing later specialisation in International Business or Management or Marketing)'],
                ['I would like to be in a job placement programme after I graduate.', 'Bachelor of Engineering (Honours) in Mechanical Engineering'],
                ['I want to work in the EU policy making in the future.', 'Bachelor of Laws (LLB) with French, German or Spanish in Law (LLB) with a Language']]

# Create an empty list to store all recommended courses
total_recommendations = []
# Create an empty list to store performance per function
total_results = []

# Loop through each functions from 'bow_jaccard', 'tfidf_cosine', 'bert_euclidean'
for function in (bow_jaccard, tfidf_cosine, bert_euclidean):

    # Create an empty list to store recommended courses per function
    recommendations = [] 
    # Create an empty list to store performance of the function
    results = []

    # Loop through each test queries
    for test in test_queries:
        # Put the query through the function
        output_indices = function(test[0])

        # Match the indices with course names
        output_names = name_lookup(output_indices)

        # Append the output to 'recommendations' list
        recommendations.append(output_names)

        # Check if the expected answer is in the top 5 recommendations
        if test[1] in output_names:
            # If it is, append 1 to 'results' list
            results.append(1)
        # If not, append 0 to to 'results' list    
        else:
            results.append(0)

    # Append the recommendations to 'total_recommendations' list        
    total_recommendations.append(recommendations)
    # Append the performance to 'total_results' list
    total_results.append(results)

# Print the performance of each function
print('Test reslts with 10 queries (0 = relevant item not present in top 5 results, 1 = relevant item present in top 5 results)')
print(f'Bag of Words + Jaccard Distance: {total_results[0]}')
print(f'TF-IDF + Cosine Similarity: {total_results[1]}')
print(f'Sentence Encoding + Euclidean Distance: {total_results[2]}')

# Print the courses recommended by each function
print('Top 5 recommendations')
print(f'Bag of Words + Jaccard Distance: {total_recommendations[0]}')
print(f'TF-IDF + Cosine Similarity: {total_recommendations[1]}')
print(f'Sentence Encoding + Euclidean Distance: {total_recommendations[2]}')


# ----- Function to print suggestions for RASA in Part 3 -----

def chat_response(input):

    # Put the query through the 'bow_jaccard' function
    output_indices = bow_jaccard(input)

    # Match the indices with course names
    output_names = name_lookup(output_indices)

    output_text = corpus_raw[output_indices[0]]

    string = f'Based on your interest, here are 5 courses you might find interesting:\n 1. {output_names[0]}\n 2. {output_names[1]}\n 3. {output_names[2]}\n 4. {output_names[3]}\n 5. {output_names[4]}'

    return string


