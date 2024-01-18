# Import required libraries
import requests
from bs4 import BeautifulSoup
import re
import math
import random
import os
import spacy

# ----- Create a Course class -----

class Course:
  def __init__(self, search_title, course_title, url):
    self.search_title = search_title
    self.course_title = course_title
    self.url = url


# ----- Extract the school names from TU Dublin website -----

# Set the string for TU Dublin Find a Course page
url_search = 'https://www.tudublin.ie/study/find-a-course/search-results/'

# Send an HTTP GET request to the URL
response = requests.get(url_search)

# Fetch and parse the data using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the form containing the checkboxes
form = soup.find('form', class_='search-results__filters')

# Extract the checkboxes and their values
checkboxes = form.find_all('input', class_='input-checkbox')

# Filter the checkboxes to 'courseSubjects' only (remove 'courseLocation')
# Create an empty list
filtered = []

# Find checkboxes that has 'courseSubjects' and append to above list
for checkbox in checkboxes:
    if checkbox.get('name') == 'courseSubjects':
        filtered.append(checkbox)

# Extract the school names from input
checkbox_values = [checkbox.get('value') for checkbox in filtered]


# ----- Create a list of URLs under all schools -----

# Set the string for TU Dublin page
url_tudublin = 'https://www.tudublin.ie'

# Create nested list containing the course URLs under all schools
# Create an empty list
courses_by_school = []

# Loop through each school names
for checkbox_value in checkbox_values:
    # Create an empty list
    courses = []

    # Send an HTTP GET request to the search page URL with school name as a parameter
    response = requests.get(url_search, {'courseSubjects': checkbox_value})

    # Fetch and parse the data using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the navigation for pagination
    nav = soup.find('nav', class_='pagination')

    # If there are no pagination, find all the course URLs and append to 'course_urls' list
    if nav == None:
        # Find all sections containing course information
        div = soup.find_all('div', class_='course-list-grid__item')
        # Loop through all courses and create URLs to their course page
        for d in div:
            # Extract the hypertext reference
            div_a = d.find('a')['href']
            # Extract the course name
            div_course = d.find('h3', class_ = 'course-list-grid__h').get_text()
            # Make the hypertext reference into a clickable URL, store it and the course name in the Course class,  and append to 'courses' list
            courses.append(Course(div_course, '', url_tudublin + div_a))

    # If there are paginations, loop through all pages and append course URLs to 'course_urls' list
    else:
        # From the navigation for pagination, find the anchor elements that include page numbers
        nav_a = nav.select('a') 

        # Extract all the numbers from the last anchor element
        max_page = re.findall(r'\d+', str(nav_a[-1]))
        
        # From the first page, find all the course URLs and append to 'course_urls' list
        # Find all the sections containing course information
        div = soup.find_all('div', class_='course-list-grid__item')

        # Loop through all the courses and create URLs to their course page
        for d in div:
            # Extract the hypertext reference
            div_a = d.find('a')['href']
            # Extract the course name
            div_course = d.find('h3', class_ = 'course-list-grid__h').get_text()
            # Make the hypertext reference into a clickable URL, store it and the course name in the Course class,  and append to 'courses' list
            courses.append(Course(div_course, '', url_tudublin + div_a))

        # Loop though the remaining pages, find all the course URLs and append to 'course_urls' list
        for page in range(2, int(max_page[-1]) + 1):

            # Send an HTTP GET request to the search page URL with school name and page as parameters
            response = requests.get(url_search,{'courseSubjects': checkbox_value, 'page':page})

            # Fetch and parse the data using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all the sections containing course information
            div = soup.find_all('div', class_='course-list-grid__item')

            # Loop through all the courses and create URLs to their course page
            for d in div:
                # Extract the hypertext reference
                div_a = d.find('a')['href']
                # Extract the course name
                div_course = d.find('h3', class_ = 'course-list-grid__h').get_text()
                # Make the hypertext reference into a clickable URL, store it and the course name in the Course class,  and append to 'courses' list
                courses.append(Course(div_course, '', url_tudublin + div_a))

    # Append all the courses from a school to 'courses_by_school' list
    courses_by_school.append(courses)


# ----- Select 50+ pages across all schools -----

# Count the number of courses for each school
num_courses_per_school = [len(school) for school in courses_by_school]

# Set a target number of pages to 50
target_sum = 50
 
# Cauculate the ratio of target numer to the total number of course URLs 
ratio = target_sum / sum(num_courses_per_school)

# Calculate how many pages per scholl should be selected in order to have the total of 50+ pages
reduced_list = [max(1, math.ceil(school * ratio)) for school in num_courses_per_school]

# Create the final list of course URLs to save text contents from
# Create an empty list
selected_courses = []

# Set the seed value for random.choices
random.seed(0)

# Loop through each school and randomly select a subset of courses based on the numbers provided in 'reduced_list'
# Zip the two lists to iterate over them simultaneously
for school, num in zip(courses_by_school, reduced_list):
    # Ranmonly select the number of courses specified
    selected_course = random.choices(school, k=num)
    # Append to 'selected_courses' list
    selected_courses.append(selected_course)


# ----- Create a corpus of 50+ .txt files -----

# Create a folder called 'corpus' if it doesn't already exist
folder_name = 'corpus'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Loop through each URL and save the text contents as .txt files
for school in selected_courses:
    for course in school:

        # Set the URL to TU Dublin Find a Course page
        course_url = course.url

        # Send an HTTP GET request to the URL
        response = requests.get(course_url)

        # Fetch and parse the data using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # If there is a course title in the notice section, store it in the Course class
        # If there is a notice section on the page
        if soup.find('div', class_="notice bg--tu-teal"):
            notice = soup.find('div', class_="notice bg--tu-teal")
            # Extract the text from the first block
            first_p_text = notice.find('p').get_text()
            # If the block text starts from "Course Title"
            if first_p_text.startswith("Course Title:"):
                # Store the text as 'course_title' in the Course class
                course.course_title = first_p_text[len("Course Title:"):].strip()
            # Otherwise leave the 'course_title' in the Course class blank
            else:
                course.course_title = ''
        # If the page does not have a notice section, leave the 'course_title' in the Course class blank
        else:
            course.course_title = ''

        # Identify the main content of the page
        main_content = soup.body.find('main')

        # Extract all the text from the main content
        text = main_content.get_text()

        # Specify the file name for saving the content
        # if the 'course_title' of the Course class is empty, use 'search_title' as the file name
        if course.course_title == '':
            file_name = course.search_title
        # otherwise use 'course_title' as the file name
        else:
            file_name = course.course_title

        # Save the extracted text to a .txt file with 'file_name' as the name
        file_path = os.path.join(folder_name, f'{file_name}.txt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text)


# ----- Descriptive analysis: Tokenization and named entity recognition -----

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Create an empty list
corpus_processed = []

# Loop through the files in the 'corpus' folder and process them using the spaCy NLP pipeline
# Set a folder path
folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'corpus')

# Loop through each file in the folder and process them
for file in os.listdir(folder_path):
    # Open each file
    with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as file:
        # Read the contents of the file
        text = file.read()
        # Process the text using the spaCy NLP pipeline
        doc = nlp(text)
        # Append to 'corpus_processed' list
        corpus_processed.append(doc)

# Descriptive analysis using named entities
# Create an empty dictionary
ner_counts = {}

# Set the initial token count
total_tokens = 0

# Loop through each document in the processed corpus
for doc in corpus_processed:
    # Loop through each named entitiy in the document
    for token in doc.ents:
        # Check if the named entity label is already in 'ner_counts' dictionary
        if token.label_ in ner_counts:
            # If the label exists, increment its count
            ner_counts[token.label_] += 1
        # If the label doesn't exist, add it with a count of 1
        else:
            ner_counts[token.label_] = 1
        # Increment the 'total_tokens' count
        total_tokens += 1

# Calculate percentages of each named entity
ner_percentages = {ent_type: count / total_tokens * 100 for ent_type, count in ner_counts.items()}

# Round the percentages to 2 decimals
ner_percentages_rounded = {ent_type: round(value, 2) for ent_type, value in ner_percentages.items()}

# Sort the percentages in descending order
sorted_ner_percentages = sorted(ner_percentages_rounded.items(), key=lambda x: x[1], reverse=True)

# Output the percentages
print(f'Named-entity recognition (%): {sorted_ner_percentages}')


# ----- Descriptive analysis: Stop words removal and part-of-speech tagging -----

# Remove stop words from 'corpus_processed'
# Create an empty list
corpus_no_stopwords = []

# Loop through each document in the processed corpus
for doc in corpus_processed:
    # Filter out stop words from the document and append to a list
    filtered_tokens = [token for token in doc if not token.is_stop]
    # Append the filtered tokens to the corpus without stop words
    corpus_no_stopwords.append(filtered_tokens)

# Descriptive analysis using part-of-speech
# Create an empty dictionary
pos_counts = {}

# Set the initial token count
total_tokens = 0

# Loop through each document in the processed corpus
for doc in corpus_no_stopwords:
    # Loop through each named entitiy in the document
    for token in doc:
        # Check if the part-of-speech is already in 'pos_counts' dictionary
        if token.pos_ in pos_counts:
            # If the label exists, increment its count
            pos_counts[token.pos_] += 1
        # If the label doesn't exist, add it with a count of 1
        else:
            pos_counts[token.pos_] = 1
        # Increment the 'total_tokens' count
        total_tokens += 1

# Calculate percentages
pos_percentages = {pos: count / total_tokens * 100 for pos, count in pos_counts.items()}

# Round the percentages to 2 decimals
pos_percentages_rounded = {pos: round(value, 2) for pos, value in pos_percentages.items()}

# Sort the percentages in descending order
sorted_pos_percentages = sorted(pos_percentages_rounded.items(), key=lambda x: x[1], reverse=True)

# Output the percentages
print(f'Part of speech annotation (%): {sorted_pos_percentages}')


# ----- Descriptive analysis: Lemmatization, data cleaning, and frequency count -----

# Lemmatize the tokens in 'corpus_no_stopwords' and remove non-alphabet letters
# Create an empty list
corpus_lemmatized = []

# Loop through each document in the processed corpus
for doc in corpus_no_stopwords:
    # Create a list to store lemmatized tokens
    lemmatized_tokens = []
    # Loop through each named entitiy in the document
    for token in doc:
        # Check if the lemmatized token consists of non-alphabet letters
        if token.lemma_.isalpha():
            # If the lemmatized token consists of non-alphabet letters, append to 'lemmatized_tokens' list
            lemmatized_tokens.append(token.lemma_.lower())
    # Append the 'lemmatized_tokens' list to 'corpus_lemmatized' list
    corpus_lemmatized.append(lemmatized_tokens)

# Frequency counts
# Create a dictionary to store word frequencies
word_frequencies = {}

# Iterate through the corpus without stop words
for i, doc in enumerate(corpus_lemmatized):
    # Loop through each named entitiy in the document
    for token in doc:
        # Check if the lemmatized token is already in 'frequency' dictionary
        if token in word_frequencies:
            # If the label exists, increment its count
            word_frequencies[token] += 1
        # If the label doesn't exist, add it with a count of 1
        else:
            word_frequencies[token] = 1

# Sort the word frequencies and select the top 30 words
sorted_frequency = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)[:30]

# Print the top 30 words and their frequencies
print(f'Frequency count: {sorted_frequency}')

# ----- Descriptive analysis: Removal of custom stop words and TF-IDF -----

# Create a list of custom stop words
custom_stop_words = ['course', 'year', 'level', 'student', 'entry', 'apply', 'study', 'minimum',
                     'english', 'work', 'award', 'module', 'time', 'application', 'tu', 'eu', 
                     'requirements', 'school', 'advanced', 'contact', 'programme', 'website', 'applicant',
                      'qqi', 'ects', 'credit']

# Remove the custom stop words from 'corpus_processed'
# Create an empty list
corpus_final = []

# Loop through each document in the processed corpus
for doc in corpus_lemmatized:
    # Filter out stop words from the document
    filtered_tokens = [token for token in doc if token not in custom_stop_words]
    # Append the filtered tokens to the corpus without stop words
    corpus_final.append(filtered_tokens)

# Calculate the TF-IDF for each document
# Create an empty dictionary to store words and their TF-IDF for each file
word_tf_idf = {}

# Create a list of file names from the original .txt files
file_names = os.listdir(folder_path)

# Loop through each document along with its index
for i, doc in enumerate(corpus_final):
    # Create an empty dictionary to store the term frequency
    tf = {}
    # Loop through each named entitiy in the document
    for token in doc:
        # Check if the lemmatized token in lower case is already in 'tf' dictionary
        if token in tf:
            # If the label exists, increment its count
            tf[token] += 1
        # If the label doesn't exist, add it with a count of 1
        else:
            tf[token] = 1

    # Calculate the inverse document frequency for each word
    # Create an empty dictionary to store the IDF
    idf = {}
    # Loop through each word in the 'tf' dictionary
    for word in tf:
        # Calculate the IDF
        idf[word] = math.log10(len(corpus_lemmatized) / (1 + sum(1 for doc in corpus_lemmatized if word in doc)))
    
    # Calculate the TF-IDF for each word
    tf_idf = {word: tf[word] * idf[word] for word in tf}
    
    # Sort the TF-IDF scores and select the top 5 words
    sorted_tf_idf = sorted(tf_idf.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Store the top 5 words in the dictionary with the file name as the key
    word_tf_idf[file_names[i]] = sorted_tf_idf

# Print the file names and their top 5 words with TF-IDF scores
for file, words in word_tf_idf.items():
    print(f'{file}:')
    for word, score in words:
        print(f'\tWord: {word}, TF-IDF: {score}')
