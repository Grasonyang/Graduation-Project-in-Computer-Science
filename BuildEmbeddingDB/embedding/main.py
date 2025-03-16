import jieba
import numpy as np
from text_rank.text_rank import TextRank
from sentence_transformers import SentenceTransformer

# 提取關鍵詞、句
def extract_keywords(text):
    # --- 提取關鍵詞 ---
    sentences = [list(jieba.cut(s)) for s in text.split('。') if s.strip()]  # 分句、分詞
    textrank_keyword = TextRank()
    textrank_keyword.build_graph(sentences)
    keywords = textrank_keyword.get_keywords(n=5)
    # print("關鍵詞:", keywords)


    # --- 提取關鍵句 ---
    sentences = [s.strip() for s in text.split('。') if s.strip()] # 分句，去除空句子
    textrank_sentence = TextRank()
    textrank_sentence.build_graph(sentences)
    key_sentences = textrank_sentence.get_key_sentences(n=2)
    # print("\n關鍵句:", key_sentences)
    return keywords, key_sentences

# 向量化
def key_words_and_sentences_to_vector(key_words, key_sentences):
    """
    關鍵詞句向量化 (使用已有的 TextRank 權重、關鍵詞向量 + 關鍵句向量)
        - 使用詞嵌入 (Word Embeddings)
            - Sentence-BERT
    可能的方法: 基於關鍵詞和關鍵句重建文本 + 句子嵌入
    """
    # 0. 載入模型
    sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    # 1-1. 關鍵詞向量化
    keyword_texts = [kw[0] for kw in key_words]
    keyword_weights = [kw[1] for kw in key_words]
    keyword_vectors = sentence_model.encode(keyword_texts)
    # 1-2. 關鍵詞加權平均
    weighted_keyword_vector = np.average(keyword_vectors, axis=0, weights=keyword_weights)
    # 2-1. 關鍵句向量化
    key_sentence_texts = [ks[0] for ks in key_sentences]
    key_sentence_scores = [ks[1] for ks in key_sentences]  # TextRank 權重
    key_sentence_vectors = sentence_model.encode(key_sentence_texts)
    # 2-2. 關鍵句加權平均
    weighted_key_sentence_vector = np.average(key_sentence_vectors, axis=0, weights=key_sentence_scores)
    # 3 組合向量 (加權平均)
    alpha = 0.5  # 可調整權重
    combined_vector = alpha * weighted_keyword_vector + (1 - alpha) * weighted_key_sentence_vector
    return combined_vector

print("Load Embedding File")