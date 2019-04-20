# building keras based model for 3 group classification
# heavily inspired by: https://www.datacamp.com/community/tutorials/deep-learning-python

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split

data = pd.read_csv('./data/cleaned.csv', encoding='utf-8')

from nltk.tokenize import TweetTokenizer # a tweet tokenizer from nltk.
tokenizer = TweetTokenizer()

def tokenize(tweet):
    try:
        tokens = tokenizer.tokenize(tweet)
        return tokens
    except:
        return 'NC'


from tqdm import tqdm
tqdm.pandas(desc="progress-bar")

# post process
data['clean_text'] = data['clean_text'].progress_map(tokenize)
data = data[data.clean_text != 'NC']
data.reset_index(inplace=True)
data.drop('index', inplace=True, axis=1)
# print(data.head())

x_train, x_test, y_train, y_test = train_test_split(np.array(data['clean_text']), np.array(data['target']),
                                                    test_size=0.2)

import gensim
from gensim.models.word2vec import Word2Vec
LabeledSentence = gensim.models.doc2vec.LabeledSentence

def labelizeTweets(tweets, label_type):
    labelized = []
    for i,v in tqdm(enumerate(tweets)):
        label = '%s_%s'%(label_type,i)
        labelized.append(LabeledSentence(v, [label]))
    return labelized

x_train = labelizeTweets(x_train, 'TRAIN')
print(x_train[0:2])
x_test = labelizeTweets(x_test, 'TEST')

print("Building word2vec matrix")
n_dim = 200
tweet_w2v = Word2Vec(size=n_dim, min_count=10)
tweet_w2v.build_vocab([x.words for x in tqdm(x_train)])
tweet_w2v.train([x.words for x in tqdm(x_train)], total_examples=tweet_w2v.corpus_count, epochs=tweet_w2v.epochs)

from sklearn.feature_extraction.text import TfidfVectorizer
print("Building tf-idf matrix")
vectorizer = TfidfVectorizer(analyzer=lambda x: x, min_df=10)
matrix = vectorizer.fit_transform([x.words for x in x_train])
tfidf = dict(zip(vectorizer.get_feature_names(), vectorizer.idf_))
print("vocab size: ", len(tfidf))


def buildWordVector(tokens, size):
    vec = np.zeros(size).reshape((1, size))
    count = 0.
    for word in tokens:
        try:
            vec += tweet_w2v[word].reshape((1, size)) * tfidf[word]
            count += 1.
        except KeyError: # handling the case where the token is not in the corpus. useful for testing.
            continue
    if count != 0:
        vec /= count
    return vec


from sklearn.preprocessing import scale
print("Scaling train vector")
train_vecs_w2v = np.concatenate([buildWordVector(z, n_dim) for z in tqdm(map(lambda x: x.words, x_train))])
train_vecs_w2v = scale(train_vecs_w2v)

print("Scaling test vector")
test_vecs_w2v = np.concatenate([buildWordVector(z, n_dim) for z in tqdm(map(lambda x: x.words, x_test))])
test_vecs_w2v = scale(test_vecs_w2v)

# build keras based model
from keras.models import Sequential
from keras.layers import Dense

print("Making model")
model = Sequential()
model.add(Dense(32, activation='relu', input_dim=200))
model.add(Dense(1, activation='sigmoid'))
model.compile(optimizer='rmsprop',
              loss='binary_crossentropy',
              metrics=['accuracy'])

print("Training model")
model.fit(train_vecs_w2v, y_train, epochs=9, batch_size=32, verbose=2)

print("Evaluating model")
score = model.evaluate(x_test, y_test, verbose=1)
print(score)

from sklearn.metrics import precision_score
y_pred = model.predict(x_test)
print(precision_score(y_test, y_pred))