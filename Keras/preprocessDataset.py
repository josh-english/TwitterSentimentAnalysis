# preprocessing dataset
# heavily inspired by: https://www.analyticsvidhya.com/blog/2018/07/hands-on-sentiment-analysis-dataset-python/
# and https://www.kaggle.com/paoloripamonti/twitter-sentiment-analysis

#import statements
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import nltk

from nltk.stem.porter import *

# DATASET CONSTANTS
DATASET_ENCODING = "ISO-8859-1"
DATASET_COLUMNS = ["target", "ids", "date", "flag", "user", "text"]

# get the data
data = pd.read_csv("./data/data.csv", encoding=DATASET_ENCODING, names=DATASET_COLUMNS)

print(data.head(5))


# clean dataset by removing text from data['text']
def remove_pattern(string, pattern):
    r = re.findall(pattern, string)
    for i in r:
        string = re.sub(i, '', string)
    return string


# remove twitter handles (@user)
data['clean_text'] = np.vectorize(remove_pattern)(data['text'], "@[\w]*")
# remove punctuation, numbers, and special characters
data['clean_text'] = data['clean_text'].str.replace("[^a-zA-Z#]", " ")
# remove short words
data['clean_text'] = data['clean_text'].apply(lambda x: ' '.join([w for w in x.split() if len(w) > 3]))
# tokenization
tokenized_tweet = data['clean_text'].apply(lambda x: x.split())
print(tokenized_tweet.head())
# stemming
stemmer = PorterStemmer()
tokenized_tweet = tokenized_tweet.apply(lambda x: [stemmer.stem(i) for i in x])
print(tokenized_tweet.head())
for i in range(len(tokenized_tweet)):
    tokenized_tweet[i] = ' '.join(tokenized_tweet[i])
data['clean_text'] = tokenized_tweet
print(data.head(5))

# # map target labels to strings
# decode_map = {0: "NEGATIVE", 2: "NEUTRAL", 4: "POSITIVE"}
#
#
# def decode_sentiment(label):
#     return decode_map[int(label)]
#
#
# data['target'] = data['target'].apply(lambda x: decode_sentiment(x))
#
# print(data.head(5))

# store preprocessed dataset in csv for easy import
data[['target', 'clean_text']].to_csv('./data/cleaned.csv', encoding='utf-8', index=False)

# create word cloud of data (optional)
all_words = ' '.join([text for text in data['clean_text']])
from wordcloud import WordCloud
wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)

#plt.interactive(False)
plt.figure(figsize=(10, 7))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis('off')
plt.show()