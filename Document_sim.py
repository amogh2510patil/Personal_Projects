# Amogh Patil
# EE19B134
# 8310733893
# CONTENT SIMILARITY DETECTION
# Lemmatization, Dictionary, Tfidf, Matrix Similarity


import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import numpy as np
from gensim import models
from gensim import corpora
from gensim.similarities import MatrixSimilarity
from string import punctuation
import time

# starting time
start = time.time()

#To remove stop words
sw = stopwords.words('English')

lemmatizer = WordNetLemmatizer()
# function to convert nltk tag to wordnet tag
def nltk_tag_to_wordnet_tag(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:          
        return None
#function to Lemmatize
def lemmatize_sentence(sentence):
    nltk_tags = nltk.pos_tag(nltk.word_tokenize(sentence))
    lemmatized_sentence = []
    for word,tag in nltk_tags:
        tag = nltk_tag_to_wordnet_tag(tag)
        if tag is None:
            #if there is no available tag, append the token as is
            lemmatized_sentence.append(word)
        else:        
            #else use the tag to lemmatize the token
            lemmatized_sentence.append(lemmatizer.lemmatize(word, tag))
    return " ".join(lemmatized_sentence)



#To open first document and obtain lemmatized sentences in an array
document_1 = []
with open ('sample3.txt') as f:
    tokens = sent_tokenize(f.read())
    for line in tokens:
        document_1.append(lemmatize_sentence(line))
#To open query document and obtain lemmatized sentences in anarray
document_2 = []
with open ('sample2.txt') as f:
    tokens = sent_tokenize(f.read())
    for line in tokens:
        document_2.append(lemmatize_sentence(line))


#To obtain words without stopwords and punctuators
word_doc1 = [[w.lower() for w in word_tokenize(text) if w not in punctuation and w not in sw] 
            for text in document_1]
word_doc2 = [[w.lower() for w in word_tokenize(text) if w not in punctuation and w not in sw]
            for text in document_2]

#Creating a dictionary with the words of document1
dictionary = corpora.Dictionary(word_doc1)
np.save('dictionary.npy', dictionary) 
#Creating the corpus using the dictionary
corpus_1 = [dictionary.doc2bow(words) for words in word_doc1]
#Finding the tfidf values of words within our corpus
tfidf_1 = models.TfidfModel(corpus_1,smartirs='ntc')
#Creating sim matrix
index=MatrixSimilarity(tfidf_1[corpus_1])

#Creating corpus for second document using the created dictionary
corpus_2 = [dictionary.doc2bow(words) for words in word_doc2]
#Finding the tfidf values within our corpus
tfidf_2 = models.TfidfModel(corpus_2,smartirs='ntc') 

#Find cosine similarity
cos_total = 0
for line in index[tfidf_2[corpus_2]]:
    cosine_sum = 0 #Holds the value of sum of cosine values(only if >=0.4) of a line of doc2 with all lines of doc1
    count = 0 #This counts number of lines which have significant cosine values(>=0.4)
    for cos_val in line:
        if cos_val >= 0.5: #Cause one line is mostly going to be similar to only a few lines ,
                           #hence if we divide the sum of cosines by the entire length of doc the value will become insignificantly small 
                           #hence i considered only those lines which are more similar than 50%
            cosine_sum = cosine_sum + cos_val
            count=count+1
    if count > 0 :
        #This value is the total of cosine values
        cos_total = cos_total + cosine_sum / count
cos_similarity = cos_total / len(document_2)
print()
print("Cosine similarity result :", np.around(cos_similarity*100,decimals=3) )

# end time
end = time.time()

# total time taken
print(f"Runtime of the program is {np.around(end - start,decimals=3)}")

