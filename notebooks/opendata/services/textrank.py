# -*- coding: utf-8 -*-
import sys
#print sys.getdefaultencoding()

"""
From this paper:
    https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf

External dependencies: nltk, numpy, networkx

Based on https://gist.github.com/voidfiles/1646117
"""

import ssl
import io
import nltk
import nltk.data
import itertools
import networkx as nx
import os
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
#import pattern.es
#from pattern.es import Sentence
import spacy
import re


__version__ = '0.1.0'
__author__ = 'Unknown'
__email__ = ''

file_path = '/home/jovyan/work/data/OpenData/validation/sentiment_ES/stop_ES'

java_path = "C:/Program Files/Java/jdk1.8.0_161/bin/java.exe"
os.environ['JAVAHOME'] = java_path

# apply syntactic filters based on POS tags
def filter_for_tags(tagged, tags=['NN', 'NNP', 'JJ']): #'NNS'
    return [item for item in tagged if item[1] in tags]


#def normalize(tagged):
#    return [(item[0].replace('.', ''), item[1]) for item in tagged]


#mio: pattern
def normalize(tagged):
    tagged_normalized = []
    for item in tagged:
        op = re.compile("(\.|\,|\:|\;|\¡|\!|\¿|\?|\-|\(|\)|\...)")
        result = op.sub("", item[0])
        tagged_normalized.append(tuple([result, item[1]]))
    return tagged_normalized


def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in [x for x in iterable if x not in seen]:
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def lDistance(firstString, secondString):
    """Function to find the Levenshtein distance between two words/sentences -
    gotten from http://rosettacode.org/wiki/Levenshtein_distance#Python
    """
    if len(firstString) > len(secondString):
        firstString, secondString = secondString, firstString
    distances = range(len(firstString) + 1)
    for index2, char2 in enumerate(secondString):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(firstString):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1],
                                             distances[index1 + 1],
                                             newDistances[-1])))
        distances = newDistances
    return distances[-1]


def buildGraph(nodes):
    """nodes - list of hashables that represents the nodes of the graph"""
    gr = nx.Graph()  # initialize an undirected graph
    gr.add_nodes_from(nodes)
    nodePairs = list(itertools.combinations(nodes, 2))

    # add edges to the graph (weighted by Levenshtein distance)
    for pair in nodePairs:
        firstString = pair[0]
        secondString = pair[1]
        levDistance = lDistance(firstString, secondString)
        gr.add_edge(firstString, secondString, weight=levDistance)

    return gr


def importPackages(download_dir):
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    nltk.download('punkt',download_dir)
    nltk.download('averaged_perceptron_tagger', download_dir)
    nltk.download('stopwords', download_dir)
    nltk.download('wordnet', download_dir)


#mio
def preprocessing(tagged):
    #print('tagged: ', tagged)
    lemmatizer = WordNetLemmatizer()
    sw_tagged = []
    #sw = stopwords.words('spanish')
    with open(file_path, 'r') as myfile:
        sw = myfile.read()

    for word in tagged:
        #mio: ignora las stopwords
        if str(word[0].encode('utf-8')) not in sw:
            #mio: lleva todo a minuscula
            processed_word = word[0].lower()
            #mio: lematiza
            processed_word = lemmatizer.lemmatize(processed_word)
            sw_tagged.append(tuple([processed_word,tagged[1]]))  
    return sw_tagged
   

def extractKeyphrases(text, k = 10, lang = 'spanish', download_dir='/data/nltk/'):
    if not os.listdir(download_dir):
        importPackages(download_dir)
    nltk.data.path.append(download_dir) #para meter la nueva direccion
    
    # 1- The text is tokenized (using nltk)
    wordTokens = word_tokenize(text, lang) #rocio
    #print('wordTokens: ', wordTokens)

    # 2- The text is annotated with POS tags  
 
    # Aquí obtenemos la lista de tokens en "tokens"
    tagged = nltk.pos_tag(wordTokens, lang = lang) #text        
    
    #print('tagged: ', tagged)
    textlist = [x[0] for x in tagged]

    # 3- To avoid excesive growth of the graph size, several synthatic filters were used (tags=['NN', 'JJ', 'NNP'])
    tagged = filter_for_tags(tagged)
    #print('filtered_tagged: ', tagged)
    
    #Mio: preprocessing:
    tagged = preprocessing(tagged)
    #print('tagged: ', tagged)

    # 3.1 Remove 'signos de putuancion con regex'
    tagged = normalize(tagged)
    #print('normalize: ', tagged)
    unique_word_set = unique_everseen([x[0] for x in tagged])
    word_set_list = list(unique_word_set)
    #print('word_set_list', word_set_list)
    
    # this will be used to determine adjacent words in order to construct
    # keyphrases with two words

    # 4- The graph is constructed (undirected unweighted graph)
    graph = buildGraph(word_set_list)
    
    #Print a figure:
    #fig, a =plt.subplots(figsize=(40, 20))
    #fig = nx.draw_networkx(G=graph, with_labels=True) # Draw the graph
    
    #Print a network:
    #nx.draw_networkx(G=graph, with_labels=True) # Draw the graph
    #plt.show()

    # 5- PageRank algorithm- initial value of 1.0, error tolerance (threshold) of 0,0001.
    calculated_page_rank = nx.pagerank(graph, weight='weight')
    #print('calculated_page_rank: ', calculated_page_rank)

    # 6- Once a final score is obtained by for each vertex in the graph, vertices are sorted in reversed order of their score, and the top T vertices in the ranking are retained for post-preprocessing.
    # Most important words in ascending order of importance
    keyphrases = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)
    #print('keyphrases_sorted: ', keyphrases)

    # 7- The number of keyphrases returned will be relative to the size of the text (a third of the number of vertices)
    aThird = len(word_set_list) // 3
    keyphrases = keyphrases[0:aThird + 1]
    #print('aThird_keyphrases', keyphrases)

    # 8- Take keyphrases with multiple words into consideration as done in the paper - if two words are adjacent in the text and are selected as keywords, join them together
    modifiedKeyphrases = set([])
    # keeps track of individual keywords that have been joined to form a keyphrase
    dealtWith = set([])
    i = 0
    j = 1
    while j < len(textlist):
        firstWord = textlist[i]
        secondWord = textlist[j]
        if firstWord in keyphrases and secondWord in keyphrases:
            keyphrase = firstWord + ' ' + secondWord
            modifiedKeyphrases.add(keyphrase)
            dealtWith.add(firstWord)
            dealtWith.add(secondWord)
        else:
            if firstWord in keyphrases and firstWord not in dealtWith:
                modifiedKeyphrases.add(firstWord)

            # if this is the last word in the text, and it is a keyword, it
            # definitely has no chance of being a keyphrase at this point
            if j == len(textlist) - 1 and secondWord in keyphrases and \
                    secondWord not in dealtWith:
                modifiedKeyphrases.add(secondWord.decode('utf-8'))

        i = i + 1
        j = j + 1

    keyphrases = list(modifiedKeyphrases)[:k] 
    result = getKeyphrasesWight(keyphrases, calculated_page_rank)
    return result


def getKeyphrasesWight(modifiedKeyphrases, calculated_page_rank): # mio
    result = []
    for keyphrase in modifiedKeyphrases:
        array = keyphrase.split(' ')
        string = ''
        if len(array) > 1:            
            for keyword in array:
                weight = calculated_page_rank.get(keyword)
                string += keyword + ' : ' + str(weight) + ' '
        else:
            weight = calculated_page_rank.get(keyphrase)
            string = keyphrase + ' : ' + str(weight)
        result.append(string.strip())
    return result


def extractSentences(text):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentenceTokens = sent_detector.tokenize(text.strip())
    graph = buildGraph(sentenceTokens)

    calculated_page_rank = nx.pagerank(graph, weight='weight')

    # most important sentences in ascending order of importance
    sentences = sorted(calculated_page_rank, key=calculated_page_rank.get,
                       reverse=True)

    # return a 100 word summary
    summary = ' '.join(sentences)
    summaryWords = summary.split()
    summaryWords = summaryWords[0:101]
    summary = ' '.join(summaryWords)

    return summary


def writeFiles(summary, keyphrases, fileName):
    "outputs the keyphrases and summaries to appropriate files"
    #print("Generating output to " + 'keywords/' + fileName)
    keyphraseFile = io.open('keywords/' + fileName, 'w')
    for keyphrase in keyphrases:
        keyphraseFile.write(keyphrase + '\n')
    keyphraseFile.close()

    #print("Generating output to " + 'summaries/' + fileName)
    summaryFile = io.open('summaries/' + fileName, 'w')
    summaryFile.write(summary)
    summaryFile.close()

    #print("-")


if __name__ == '__main__':
    # retrieve each of the articles
    articles = os.listdir("articles")
    for article in articles:
        #print('Reading articles/' + article)
        articleFile = io.open('articles/' + article, 'r')
        text = articleFile.read()
        keyphrases = extractKeyphrases(text)
        summary = extractSentences(text)
        writeFiles(summary, keyphrases, article)
