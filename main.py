import subprocess
import os
from tkinter import *
import ast,csv
from tkinter import ttk
f = open('books.jl', 'r+')
def deleteContent(f):
    f.seek(0)
    f.truncate()
deleteContent(f)
print("Check out what people feel about any book!")
a = input("Enter name of book\t")
goodreads = 'scrapy crawl good -a category={} -o books.jl'.format(a.replace(" ", "+"))
subprocess.call('/bin/bash -c "$GREPDB"', shell=True, env={'GREPDB': goodreads})
path = 'pos'
import re
def to_words(raw_review):
        letters_only = re.sub("[^a-zA-Z]", " ", raw_review)
        words = letters_only.lower().split()
        return( " ".join( words ))
import pandas as pd
train = pd.read_csv("reviews.csv", header=0, quoting=3)

from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer(analyzer = "word",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             max_features = 5000)

train_data_features = vectorizer.fit_transform(train['Review'])
train_data_features = train_data_features.toarray()
vocab = vectorizer.get_feature_names()

#Using random forest to fit the data
from sklearn.ensemble import RandomForestClassifier
forest = RandomForestClassifier(n_estimators = 100)
forest = forest.fit(train_data_features, train["Sent"] )

test = pd.read_csv("book_rev.csv", header=0, quoting=3)
test = test[pd.notnull(test['Review'])]
test_data_features = vectorizer.transform(test['Review'])
test_data_features = test_data_features.toarray()
result = forest.predict(test_data_features)

# Copy the results to a pandas dataframe
output = pd.DataFrame( data={"Rev":test["Review"], "sentiment":result, "rating":test['Rating']} )

# Use pandas to write the comma-separated output file
output.to_csv( "Bag_of_Words_model.csv", index=False, quoting=3 )

#---------------------Creating csv file from text files
# for filename in os.listdir(path):
#     file = open("pos/"+filename,"r")
#     prod_dict = {'Review':to_words(file.read()), 'Sent':1}
#     with open('reviews.csv', 'a', newline='') as csvfile:
#         headings = ['Review', 'Sent']
#         writer = csv.DictWriter(csvfile, fieldnames=headings)
#         writer.writerow(prod_dict)
