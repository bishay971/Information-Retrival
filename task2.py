# Import required libraries
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


# load the excel dataset.
#data = pd.read_excel('C:/Users/bishe/OneDrive/Desktop/Personal/Softwerica/Information Retrival/cluster.xlsx')
# Get the current working directory

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)
current_directory = os.getcwd()

# Create the file path for cluster.csv
file_path = os.path.join(current_directory, 'cluster.xlsx')
data = pd.read_excel(file_path)
df = pd.DataFrame(data)

####@@@@ Text Preprocessing
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    words = word_tokenize(text)
    filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
    return ' '.join(filtered_words)

df['Processed_Text'] = df['Sentence'].apply(preprocess_text)

# split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['Processed_Text'], 
                                                    df['category'],
                                                    test_size=0.2,
                                                    stratify=df['category'],
                                                    random_state=9)

# using the Term Frequency-Inverse Document Frequency (TF-IDF) representation
vector = TfidfVectorizer(stop_words='english', 
                         ngram_range = (1,2),
                         min_df = 3,
                         max_df = 1.,
                         max_features = 10000)

####@@@@ function to fit and evaluate a machine learning model using a pipeline

def fit_model(model, model_name):
    line = Pipeline([('vectorize', vector), (model_name, model)])
    
    output = cross_validate(line, 
                            X_train, 
                            y_train, 
                            cv = KFold(shuffle = True, 
                                       n_splits = 3,  
                                       random_state = 9),
                            scoring = ('accuracy', 'f1_weighted','precision_weighted','recall_weighted'),           
                            return_train_score=True)
    return output

# Join training and test datasets
X = pd.concat([X_train, 
               X_test])
y = pd.concat([y_train, 
               y_test])

####@@@@ function fit a specified classifier to the provided training data

def create_and_fit(clf, x, y):
    best_clf = clf
    pipeline = Pipeline([('vectorize', vector), ('model', best_clf)])
    return pipeline.fit(x, y)

# Create model
model_classifier = create_and_fit(MultinomialNB(), X, y)

def classify_text(classifier, text):
    category = classifier.predict([text])
    return category[0]

# Get input text from the user
input_text = input("Enter text to be classified: ")

# Classify the input text
result_category = classify_text(model_classifier, input_text)

print("The input text belongs to category:", result_category)