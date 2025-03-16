from annoy import AnnoyIndex
import os
from embedding.main import extract_keywords, key_words_and_sentences_to_vector
import json

def search_vector(ann_file, query_vector, num_neighbors):
    # 假設向量的維度是 384
    vector_dim = 384
    index = AnnoyIndex(vector_dim, 'angular')
    index.load(ann_file)  # 加載 .ann 文件

    # 進行向量搜尋
    nearest_neighbors = index.get_nns_by_vector(query_vector, num_neighbors)
    return nearest_neighbors

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    ann_file = os.path.join(current_directory, 'db/test.ann')
    id_to_data_file = os.path.join(current_directory, 'db/id_to_data.json')
    
    num_neighbors = 10  # 您想要找到的最近鄰數量

    # 假設您有一個查詢句子
    query_sentence = "地震"
    
    # 提取關鍵詞
    key_words, key_sentences = extract_keywords(query_sentence)
    
    # 將關鍵詞和句子轉換為向量
    query_vector = key_words_and_sentences_to_vector(key_words, key_sentences)
    
    neighbors = search_vector(ann_file, query_vector, num_neighbors)
    print("Nearest neighbors:", neighbors)
    
    # 加載 id_to_data 和 id_to_label
    with open(id_to_data_file, 'r') as f:
        id_to_data = json.load(f)

    # 找出對應的數據和標籤
    for neighbor in neighbors:
        data = id_to_data[str(neighbor)]
        print(f"NeighborID: {neighbor}\n")
        print(f"Content: {data[0]} Label: {data[1]}\n")
        print(f"Key words: {data[2]}\n")
        print(f"Key sentences: {data[3]}\n")
        print("=====\n")
    