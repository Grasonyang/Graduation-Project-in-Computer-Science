import csv
import os
import sys
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)

import annoy
from embedding.main import extract_keywords, key_words_and_sentences_to_vector

# 1. 讀取數據
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, 'data/test1.csv')

with open(file_path, 'r', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    data = list(reader)

feature_vectors = []
labels = []
id_to_data = {}
for i, row in enumerate(data) :
    """
    label: 0 (true), 1 (fake), 2 (測試集標註)
    """
    content, label = row
    if(label == '0'):
        labels.append('true')
        key_words, key_sentences = extract_keywords(content)
        key_vector = key_words_and_sentences_to_vector(key_words, key_sentences)
        feature_vectors.append(key_vector)
        id_to_data[i] = (content, 'true', key_words, key_sentences)
    elif(label == '1'):
        labels.append('false')
        key_words, key_sentences = extract_keywords(content)
        key_vector = key_words_and_sentences_to_vector(key_words, key_sentences)
        feature_vectors.append(key_vector)
        id_to_data[i] = (content, 'false', key_words, key_sentences)
    # break
print(feature_vectors)
# build annoy index
f = len(feature_vectors[0])
t = annoy.AnnoyIndex(f, 'angular')

for i, v in enumerate(feature_vectors):
    t.add_item(i, v)

t.build(10)

# save index
# ensure the directory exists
os.chdir(current_directory)
os.makedirs('db', exist_ok=True)
t.save('db/test.ann')
with open('db/vector_dim.txt', 'w') as f_dim:
    f_dim.write(str(f))

import json
# save id_to_data
with open('db/id_to_data.json', 'w') as f:
    json.dump(id_to_data, f)