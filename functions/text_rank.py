import numpy as np
import torch


import jieba
class TextRank_chinese:
    def __init__(self, damping_factor=0.85, max_iter=200, tol=1e-4):
        self.damping_factor = damping_factor  # 阻尼係數
        self.max_iter = max_iter          # 最大迭代次數
        self.tol = tol                   # 收斂閾值
        self.graph = None

    def build_graph(self, sentences):
        """
        構建詞圖或句圖。

        Args:
            sentences:  列表，每個元素是一個分詞後的句子 (詞語列表) 或原始句子。
                       如果是提取關鍵詞，則是分詞後的句子列表；
                       如果是提取關鍵句，則是原始句子列表。
        """
        # 1. 建立詞彙表 (或句子索引)
        if isinstance(sentences[0], list):  # 提取關鍵詞
            vocab = set()
            for sentence in sentences:
                vocab.update(sentence)
            self.word_to_idx = {word: i for i, word in enumerate(vocab)}
            self.idx_to_word = {i: word for word, i in self.word_to_idx.items()}
            num_nodes = len(vocab)
            
            # 2. 建立鄰接矩陣 (使用 PyTorch Tensor)
            self.graph = torch.zeros((num_nodes, num_nodes))
            for sentence in sentences:
                for i in range(len(sentence)):
                    for j in range(i + 1, len(sentence)):
                        word1_idx = self.word_to_idx[sentence[i]]
                        word2_idx = self.word_to_idx[sentence[j]]
                        self.graph[word1_idx, word2_idx] += 1
                        self.graph[word2_idx, word1_idx] += 1  # 無向圖

        else:  # 提取關鍵句
            num_nodes = len(sentences)
            self.graph = torch.zeros((num_nodes, num_nodes))
            self.sentences = sentences # 儲存原始句子

            # 計算句子相似度 (這裡用簡單的詞袋模型 + Jaccard 相似度)
            sentence_tokens = [set(jieba.lcut(s)) for s in sentences]  # 分詞
            for i in range(num_nodes):
                for j in range(i + 1, num_nodes):
                    intersection = len(sentence_tokens[i].intersection(sentence_tokens[j]))
                    union = len(sentence_tokens[i].union(sentence_tokens[j]))
                    if union > 0:
                        similarity = intersection / union
                        self.graph[i, j] = similarity
                        self.graph[j, i] = similarity

        # 3. 將每一列歸一化 (轉成機率)
        for i in range(num_nodes):
            row_sum = torch.sum(self.graph[i])
            if row_sum > 0:
                self.graph[i] /= row_sum

    def train(self):
        """
        執行 TextRank 算法。
        """
        scores = torch.ones(self.graph.shape[0]) / self.graph.shape[0]  # 初始化分數

        for _ in range(self.max_iter):
            prev_scores = scores.clone()
            scores = (1 - self.damping_factor) + self.damping_factor * torch.matmul(self.graph.T, scores)

            # 檢查是否收斂
            if torch.sum(torch.abs(scores - prev_scores)) < self.tol:
                break

        return scores
    
    def get_keywords(self, n=10, word_min_len=2):
        """
        提取關鍵詞。
        Args:
            n:              返回關鍵詞數量。
            word_min_len:   最小詞語長度。
        """
        
        scores = self.train()
        # 根據分數排序並取得對應詞語
        top_indices = torch.argsort(scores, descending=True)
        keywords = []
        for idx in top_indices:
            word = self.idx_to_word[idx.item()]
            if len(word) >= word_min_len:
                keywords.append((word, scores[idx.item()].item()))
            if len(keywords) >= n:
                break
        return keywords

    def get_key_sentences(self, n=3):
      """
      提取關鍵句
      Args:
          n: 返回關鍵句的數量
      """
      scores = self.train()
      top_indices = torch.argsort(scores, descending=True)
      key_sentences = []
      for idx in top_indices[:n]:
          key_sentences.append((self.sentences[idx.item()], scores[idx.item()].item()))
      return key_sentences

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

class TextRank_english:
    def __init__(self, damping_factor=0.85, max_iter=200, tol=1e-4):
        self.damping_factor = damping_factor  # Damping factor
        self.max_iter = max_iter            # Maximum number of iterations
        self.tol = tol                      # Convergence threshold
        self.graph = None
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.sentences = []

    def build_graph(self, text, for_keywords=False, window_size=2):
        """
        Builds the graph for keywords or key sentences.

        Args:
            text: The input text (string).
            for_keywords: If True, builds a word graph for keyword extraction.
                          If False, builds a sentence graph for key sentence extraction.
            window_size: The window size for word co-occurrence (for keyword extraction).
        """
        if for_keywords:
            tokens = [word.lower() for word in word_tokenize(text) if word.isalnum() and word.lower() not in stop_words]
            vocab = list(set(tokens))
            self.word_to_idx = {word: i for i, word in enumerate(vocab)}
            self.idx_to_word = {i: word for word, i in self.word_to_idx.items()}
            num_nodes = len(vocab)
            self.graph = torch.zeros((num_nodes, num_nodes))

            for i in range(len(tokens)):
                for j in range(i + 1, min(len(tokens), i + 1 + window_size)):
                    word1 = tokens[i]
                    word2 = tokens[j]
                    if word1 in self.word_to_idx and word2 in self.word_to_idx:
                        idx1 = self.word_to_idx[word1]
                        idx2 = self.word_to_idx[word2]
                        self.graph[idx1, idx2] += 1
                        self.graph[idx2, idx1] += 1  # Undirected graph

        else:  # Extract key sentences
            self.sentences = sent_tokenize(text)
            num_nodes = len(self.sentences)
            self.graph = torch.zeros((num_nodes, num_nodes))
            sentence_tokens = [set(word_tokenize(s.lower())) for s in self.sentences]

            for i in range(num_nodes):
                for j in range(i + 1, num_nodes):
                    intersection = len(sentence_tokens[i].intersection(sentence_tokens[j]))
                    union = len(sentence_tokens[i].union(sentence_tokens[j]))
                    if union > 0:
                        similarity = intersection / union
                        self.graph[i, j] = similarity
                        self.graph[j, i] = similarity

        # Normalize the graph rows
        for i in range(num_nodes):
            row_sum = torch.sum(self.graph[i])
            if row_sum > 0:
                self.graph[i] /= row_sum

    def train(self):
        """
        Executes the TextRank algorithm.
        """
        num_nodes = self.graph.shape[0]
        scores = torch.ones(num_nodes) / num_nodes  # Initialize scores

        for _ in range(self.max_iter):
            prev_scores = scores.clone()
            scores = (1 - self.damping_factor) + self.damping_factor * torch.matmul(self.graph.T, scores)

            # Check for convergence
            if torch.sum(torch.abs(scores - prev_scores)) < self.tol:
                break

        return scores

    def get_keywords(self, n=10, min_word_len=2):
        """
        Extracts keywords.
        Args:
            n: The number of keywords to return.
            min_word_len: The minimum length of a keyword.
        """
        scores = self.train()
        top_indices = torch.argsort(scores, descending=True)
        keywords = []
        for idx in top_indices:
            word = self.idx_to_word[idx.item()]
            if len(word) >= min_word_len:
                keywords.append((word, scores[idx.item()].item()))
            if len(keywords) >= n:
                break
        return keywords

    def get_key_sentences(self, n=3):
        """
        Extracts key sentences.
        Args:
            n: The number of key sentences to return.
        """
        scores = self.train()
        top_indices = torch.argsort(scores, descending=True)
        key_sentences = []
        for idx in top_indices[:n]:
            key_sentences.append((self.sentences[idx.item()], scores[idx.item()].item()))
        return key_sentences


print("Load TextRank File")