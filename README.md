# :speech_balloon: Retrieval Augmented GPT: Project Overview
* Scraped [the TU Dublin course website](http://www.tudublin.ie/study/find-a-course/) using Beautiful Soup
* Built a conversational assistant by connecting an LLM with a custom vector database using ChromaDB and Langchain
* Compared it with a slot-based dialogue management using Rasa framework

## Code and Resources Used
* Python Version: Python 3.11.7
* Packages: requests, BeautifulSoup, re, math, random, os, spacy, nltk, sklearn, numpy, sentence_transformers, chromadb, langchain
* LLM: OpenAI's GPT 3.5 Turbo

## Scraping and Data Analysis

## Information Retrieval and Slot-Based Dialogue Management
* [information_retrieval.py](https://github.com/ayanoyamamoto0/retrieval_augmented_gpt/blob/main/information_retrieval.py) compares 3 different combinations of document encoding and similarity measurement approaches (Bag of words with Jaccard distance, TF-IDF with cosine similarity, Sentence encoding with Euclidean distance)
* [rasa_project](https://github.com/ayanoyamamoto0/retrieval_augmented_gpt/tree/main/rasa_project) trains a co

## LLM with Custom Database
* [converstaional_assistant.py](https://github.com/ayanoyamamoto0/retrieval_augmented_gpt/blob/main/conversational_assistant.py) transforms the corpus into a vector database
* Creates a chatbot which answers questions based on the retrieved documents from the database
