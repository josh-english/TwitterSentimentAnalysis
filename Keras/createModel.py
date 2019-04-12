# building keras based model for 3 group classification
# heavily inspired by: https://www.datacamp.com/community/tutorials/deep-learning-python

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

data = pd.read_csv('./data/cleaned.csv', encoding='utf-8')

print(data.head())

x_train, x_test, y_train, y_test = train_test_split(np.array(data['clean_text']), np.array(data['target']), test_size=0.2)

# scale data
scaler = StandardScaler().fit(x_train)
x_train = scaler.transform(x_train)
x_test = scaler.transform(x_test)

# build keras based model
from keras.models import Sequential
from keras.layers import Dense

model = Sequential()
model.add(Dense(12, activation='relu', input_shape=(1600000,)))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

model.fit(x_train, y_train, epochs=100, batch_size=16000, verbose=1)

score = model.evaluate(x_test, y_test, verbose=1)
print(score)

from sklearn.metrics import precision_score
y_pred = model.predict(x_test)
print(precision_score(y_test, y_pred))