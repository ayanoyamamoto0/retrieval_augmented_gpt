# Import required libraries
import chromadb
from chromadb.utils import embedding_functions
import os
import getpass
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI


# ----- Make the corpus into vector database -----

# Create a client object to interact with the Chroma database
chroma_client = chromadb.Client()

# Please update below to your own API key
os.environ['OPENAI_API_KEY'] = 'API key'

# Set the path to the corpus folder
corpus_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'corpus')

# Load all the documents in the corpus folder
# Create an empty list to store the raw text of each document
raw_documents = []

# Loop through each file in the corpus folder
for filename in os.listdir(corpus_folder):
    # Create the full file path by joining the 'corpus_folder' path and the filename
    filepath = os.path.join(corpus_folder, filename)
    # Create a TextLoader object to load the text from the file
    loader = TextLoader(filepath, encoding = 'UTF-8')
    # Load the text from the file and append it to the 'raw_documents' list
    raw_documents.append(loader.load())

# Split the documents into smaller chunks of 3600 characters with no overlap
text_splitter = CharacterTextSplitter(chunk_size = 3600, chunk_overlap = 0)

# Create a flat list of all the chunks from all the documents
documents_list = [chunk for doc in raw_documents for chunk in text_splitter.split_documents(doc)]

# Create a vector database by processing the documents and generating embeddings using OpenAIEmbeddings
vectordb = Chroma.from_documents(documents = documents_list, embedding = OpenAIEmbeddings(), persist_directory = 'db')


# ----- Chatbot -----

# Create an instance of a ChatOpenAI object using the with the 'gpt-3.5-turbo' model with temperature 0
model = ChatOpenAI(
    temperature = 0,
    model_name = 'gpt-3.5-turbo',
)

# Create a retriever from the 'vectordb' database
retriever = vectordb.as_retriever()

# Create a RetrievalQA object to answer questions based on the retrieved documents
qa = RetrievalQA.from_llm(llm = model, retriever = retriever)

# Print a greeting string to prompt user input
print("Hello! I'm here to help you find the perfect course for you at TU Dublin. What are you passionate about or what field would you like to study? (When you want to stop the conversation, please type 'end' or 'exit'.)")

# Create an interactive loop for user to ask questions, with option to end conversation
# Initiate an infinite loop
while True:
    # Receive the user's input
    question = input()
    
    # Check if the user wants to end the conversation
    if question.lower() == "end" or question.lower() == "exit":
        # If so, print a message to end conversation
        print("Thank you for your interest in TU Dublin! If you have any further questions or would like more information, please don't hesitate to reach out to us. Have a great day!")
        # Exit the loop
        break  
    # If the user does not want to end the conversation, continue
    else:
        # Pass the user input to the RetrievalQA object
        result = qa({"query": question})
        # Print the result
        print(result["result"])
