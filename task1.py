# Importing required libraries
import csv
import os
import json
import requests
from bs4 import BeautifulSoup

# library for string processing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)
current_directory = os.getcwd()

# get request from url
url="https://pureportal.coventry.ac.uk/en/organisations/centre-for-health-and-life-sciences"
response = requests.get(url)

####@@@@ Crawling Function

def crawl_and_extract(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        publications = []

        # Extract relevant information from the page
        # Replace these selectors with the actual ones from the target website
        for publication_elem in soup.find_all("div", class_= "result-container"):
            title = publication_elem.find("h3" , class_="title").text.strip()
            authors = [author.text.strip() for author in publication_elem.find_all("a", class_="link person")]
            year = publication_elem.find("span", class_="date")
            publication_year = year.text.strip() if year else "NA"
            publication_link = publication_elem.find("a", class_="link")['href']
            author_profile_link = publication_elem.find('a', class_ = 'link person')['href']

            publications.append({
                'title': title,
                'authors': ', '.join(authors),
                'publication_year': publication_year,
                'publication_link': publication_link,
                'author_profile_link': author_profile_link
            })

        # Save publications to CSV file
        csv_filename = os.path.join(current_directory, 'publications.csv')
        #csv_filename = 'C:/Users/bishe/OneDrive/Desktop/Personal/Softwerica/Information Retrival/publications.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'authors', 'publication_year', 'publication_link', 'author_profile_link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write data
            for publication in publications:
                writer.writerow(publication)  
            
        return publications
    
    return None

# Storing the crawled information
result = crawl_and_extract(url)

####@@@@ Function to process the string.

def remove_stop_words(input_str):
    # Tokenize the input string
    words = nltk.word_tokenize(input_str)

    # Get the English stop words
    stop_words = set(stopwords.words('english'))

    # Remove stop words from the list of words
    filtered_words = [word for word in words if word.lower() not in stop_words]

    # Join the filtered words back into a string
    result_str = ' '.join(filtered_words)

    return result_str

####@@@@ Construction of Inverted Index based on titles.

def construct_inverted_index(publications):
    inverted_index = {}

    for idx, publication in enumerate(publications):
        title_terms_extract = publication['title'].lower()
        title_terms = remove_stop_words(title_terms_extract).split()
        #author_terms = publication['authors'].lower().split()

        # Indexing terms in the title
        for term in title_terms:
            if term not in inverted_index:
                inverted_index[term] = [idx]
            else:
                inverted_index[term].append(idx)

    return inverted_index

# Example usage with the result from the crawl_and_extract function
inverted_index = construct_inverted_index(result)

# Convert the inverted index to JSON format
json_inverted_index = json.dumps(inverted_index, indent=2)

####@@@@ Finding the document based on user input
csv_filename = os.path.join(current_directory, 'publications.csv')
csv_file_path = csv_filename

def search_csv(input_str, inverted_index):
    words = input_str.split()
    #print(words)
    # Initialize an empty set to store the matching document indices
    matching_documents = set()

    # Iterate through each word in the input
    for word in words:
        # Check if the word is present in the inverted index
        if word in inverted_index.keys():
            # If present, add the document indices to the set
            matching_documents.update(inverted_index[word])
            #print(word)

    # Read the CSV file and return all rows for the matching documents
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        result_rows = [row for index, row in enumerate(reader) if index in matching_documents]

    return result_rows

# Example usage
inverted_index_json = json_inverted_index

inverted_index = json.loads(inverted_index_json)
#print(inverted_index)

user_input = input("Enter search query: ")
result = search_csv(user_input, inverted_index)

if result:
    for row in result:
        print(row)
else:
    print("No matching documents found.")
