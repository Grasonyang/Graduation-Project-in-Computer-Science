from text_rank import TextRank
import jieba

# 準備中文文本
text = """
自然语言处理是人工智能领域的一个重要方向。它研究能实现人与计算机之间用自然语言进行有效通信的各种理论和方法。
自然语言处理是一门融语言学、计算机科学、数学于一体的科学。因此，这一领域的研究将涉及自然语言，即人们日常使用的语言，
所以它与语言学的研究有着密切的联系，但又有重要的区别。自然语言处理并不是一般地研究自然语言，
而在于研制能有效地实现自然语言通信的计算机系统，特别是其中的软件系统。因而它是计算机科学的一部分。
"""

# --- 提取關鍵詞 ---
sentences = [list(jieba.cut(s)) for s in text.split('。') if s.strip()]  # 分句、分詞
textrank_keyword = TextRank()
textrank_keyword.build_graph(sentences)
keywords = textrank_keyword.get_keywords(n=5)
print("關鍵詞:", keywords)


# --- 提取關鍵句 ---
sentences = [s.strip() for s in text.split('。') if s.strip()] # 分句，去除空句子
textrank_sentence = TextRank()
textrank_sentence.build_graph(sentences)
key_sentences = textrank_sentence.get_key_sentences(n=2)
print("\n關鍵句:", key_sentences)