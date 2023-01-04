# -*- coding: utf-8 -*-
"""CBOW training.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YC5vEXCKiFZy1XmU6VWoceyzK4275Urb
"""
pip install -r requirements.txt

import re
import pandas as pd
import numpy as np
import tensorflow as tf
import nltk
nltk.download("punkt")
from nltk import word_tokenize
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Embedding,Lambda
import tensorflow.keras.backend as k

df = pd.read_csv("/Restaurant_Reviews.tsv",sep = "\t")
x = df.iloc[:,0].astype(str).values

"""#Training  Continuous Bag Of Words model

in this model we will take a target word between some context words in a sentence
"""

class CBOW:
  def __init__(self,window_size,emb_dim):
    self.window_size = window_size
    self.emb_dim = emb_dim

  def data_cleaning(self,sentences):
    # this function takes list of sentences as input and remove URL from them(which can be inside tweets) and return cleaned sentences
    cleaned_list = []
    for text in sentences:
      list_2 = []
      for w in text.split():
        if w != "URL":
          list_2.append(w)
      string = " ".join(list_2)
      cleaned_list.append(string)
    return cleaned_list
  
  def data_clean(self,sentence):
    # this function will remove unwanted marks from sentences like punctuations and dots etc.
    cleaned_sentences = self.data_cleaning(sentence)
    list = []
    for text in cleaned_sentences:
      string = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z\t])|(\w+:\/\/\S+)"," ",text).lower().split()
      string = " ".join(string)
      list.append(string)
    return list
  
  def helper_function(self,sentences):
    # this function will take list of sentences and take each sentence tokenize them in words in same order and put them in a list named dictionary
    # and return two lists dictionary and vocab,dictionary is a list containing words of every sentence and vocab is a list containing unique words from all sentences 
    vocabs = []
    dictionary = []
    for text in sentences:
      words = word_tokenize(text)
      vocabs.append(words)
    for vocab in vocabs:
      for words in vocab:
        dictionary.append(words)
    vocab = set(dictionary)
    return vocab,dictionary
   
  def get_windows(self,dictionary,c):
    # this function takes dictionary and c(window size) as input,and go inside dictionary choose a target words and c words left to target word and c words right to target word
    # is choosen as context words.
    # it returns a list named data which contains tuples and inside that tuples there will be list of context words and their corresponding target word
    i = c
    data = []
    while(i<len(dictionary)-c):
      target_words = dictionary[i]
      context_words = dictionary[i-c:i] + dictionary[(i+1):(i+1+c)]
      data.append((context_words,target_words))
      i = i+1
    return data
  
  def data_preparation(self,final_data,vocab):
    # this function will take final_data and vocab as input where final_data is output of get_windows function and vocab is list of unique words, now this function wil create
    # two dictionaries word_to_index and index_to_word to assign each word a integer and also their reverse this is done because all our calculation will be on numerical data
    # this function will return contextual_data and target_data where contextual_data is a list containing lists of integers representing a word
    vocab_size = len(vocab)
    word_to_index = {word: i for i, word in enumerate(vocab)}
    index_to_word = {i: word for i, word in enumerate(vocab)}
    target_data = []
    contextual_data = []
    for context,target in final_data:
      sequence = [word_to_index[w] for w in context]
      contextual_data.append(sequence)
      data = to_categorical(word_to_index[target],vocab_size,dtype = "int8")
      target_data.append(data)
    return contextual_data,target_data
  
  def train(self,x):
    # this function will wrap up all function and train our model and for it we will create a neural network in this we give contextual_data as input 
    # and feed it to embedding layer which wil turns every integer into a 200 dimensional vector then next layer is a custom layer which will take mean
    # of all context_words in a list(in our case it is 4) and after this layer our data have dimension(None,200) and then next layer is softmax layer is
    # softmax layer which gives probability of every word in vocab to target word and it will be our output.
    # this function will return weights which will contains a 200D vector for every word and we can use it further in various task
    sentences_list = self.data_clean(x)
    vocab,dictionary = self.helper_function(sentences_list)
    window_size = self.window_size
    emb_dim = self.emb_dim
    data = self.get_windows(dictionary,window_size)
    vocab_size = len(vocab)
    contextual_data,target_data  = self.data_preparation(data,vocab)
    x_train = np.asarray(contextual_data).astype(np.float32)
    y_train = np.array(target_data)
    model = Sequential()
    model.add(Embedding(input_dim = vocab_size,output_dim = emb_dim,input_length = 2*window_size))  # input_length is length of each input sequences
    model.add(Lambda(lambda x : k.mean(x,axis=1),output_shape=(emb_dim,))) #mean along axis=1 means mean of 2Darray (4,200) along column_wise
    model.add(Dense(vocab_size,activation = "softmax"))
    model.compile(optimizer = "adam", loss = "categorical_crossentropy", metrics = ["accuracy"])
    model.fit(x = x_train, y = y_train, batch_size =64, epochs = 50)
    weights = model.get_weights()[0]
    return weights

window_size = 2
emb_dim = 200
model = CBOW(window_size,emb_dim)
weights = model.train(x)

