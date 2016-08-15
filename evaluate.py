# -*- coding: utf-8 -*-
import ConfigParser
import numpy
import codecs
import sys
import time
import random 
import math
import os
from copy import deepcopy
import json
from numpy.linalg import norm
from numpy import dot
from scipy.stats import spearmanr

lp_map = {}
lp_map["english"] = u"en_"
lp_map["german"] = u"de_"
lp_map["italian"] = u"it_"
lp_map["russian"] = u"ru_"


def normalise_word_vectors(word_vectors, norm=1.0):
    """
    This method normalises the collection of word vectors provided in the word_vectors dictionary.
    """
    for word in word_vectors:
        word_vectors[word] /= math.sqrt((word_vectors[word]**2).sum() + 1e-6)
        word_vectors[word] = word_vectors[word] * norm
    return word_vectors


def load_word_vectors(file_destination, language):
    """
    This method loads the word vectors from the supplied file destination. 
    It loads the dictionary of word vectors and prints its size and the vector dimensionality. 
    """
    print "Loading word vectors from", file_destination
    word_dictionary = {}

    try:
        f = codecs.open(file_destination, 'r', 'utf-8') 

        for line in f:
            line = line.split(" ", 1)   
            key = line[0].lower()
            if lp_map[language] not in key:
                key = lp_map[language] + key
            try:
                transformed_key = unicode(key)
            except:
                print "CANT LOAD", transformed_key
            word_dictionary[transformed_key] = numpy.fromstring(line[1], dtype="float32", sep=" ")
    except:
        print "Word vectors could not be loaded from:", file_destination
        return {}

    print len(word_dictionary), "vectors loaded from", file_destination     

    return normalise_word_vectors(word_dictionary)


def distance(v1, v2, normalised_vectors=False):
    """
    Returns the cosine distance between two vectors. 
    If the vectors are normalised, there is no need for the denominator, which is always one. 
    """
    if normalised_vectors:
        return 1 - dot(v1, v2)
    else:
        return 1 - dot(v1, v2) / ( norm(v1) * norm(v2) )


def simlex_analysis(word_vectors, language="german", source="simlex"):
    """
    This method computes the Spearman's rho correlation (with p-value) of the supplied word vectors. 
    The method also prints the gold standard SimLex-999 ranking to results/simlex_ranking.txt, 
    and the ranking produced using the counter-fitted vectors to results/counter_ranking.txt 
    """
    pair_list = []
    if source == "simlex":
        fread_simlex=codecs.open("evaluation/simlex-" + language + ".txt", 'r', 'utf-8')
    else:
        fread_simlex=codecs.open("evaluation/ws-353/wordsim353-" + source + ".txt", 'r', 'utf-8') # specify english, english-rel, etc.

    line_number = 0
    for line in fread_simlex:

        if line_number > 0:
            tokens = line.split()
            word_i = tokens[0].lower()
            word_j = tokens[1].lower()
            score = float(tokens[2])

            word_i = lp_map[language] + word_i
            word_j = lp_map[language] + word_j

            if word_i in word_vectors and word_j in word_vectors:
                pair_list.append( ((word_i, word_j), score) )
            else:
                pass
        line_number += 1

    pair_list.sort(key=lambda x: - x[1])

    coverage = len(pair_list)

    extracted_list = []
    extracted_scores = {}

    for (x,y) in pair_list:

        (word_i, word_j) = x
        current_distance = distance(word_vectors[word_i], word_vectors[word_j]) 
        extracted_scores[(word_i, word_j)] = current_distance
        extracted_list.append(((word_i, word_j), current_distance))

    extracted_list.sort(key=lambda x: x[1])

    spearman_original_list = []
    spearman_target_list = []

    for position_1, (word_pair, score_1) in enumerate(pair_list):
        score_2 = extracted_scores[word_pair]
        position_2 = extracted_list.index((word_pair, score_2))
        spearman_original_list.append(position_1)
        spearman_target_list.append(position_2)

    spearman_rho = spearmanr(spearman_original_list, spearman_target_list)

    return round(spearman_rho[0], 3), coverage


def main():
    """
    The user can provide the location of the config file as an argument. 
    If no location is specified, the default config file (experiment_parameters.cfg) is used.
    """
    try:
        word_vector_location = sys.argv[1]
        language = sys.argv[2]
        word_vectors = load_word_vectors(word_vector_location, language)
    except:
        print "USAGE: python code/simlex_evaluation.py word_vector_location language"
        return


    print "\n============= Evaluating word vectors for language:", language, " =============\n"

    simlex_score, simlex_coverage = simlex_analysis(word_vectors, language)
    print "SimLex-999 score and coverage:", simlex_score, simlex_coverage
    
    # WordSim Validation scores:
    c1, cov1 = simlex_analysis(word_vectors,language, source=language)
    c2, cov2 = simlex_analysis(word_vectors,language, source=language + "-sim")
    c3, cov3 = simlex_analysis(word_vectors,language, source=language + "-rel")
    print "WordSim overall score and coverage:", c1, cov1
    print "WordSim Similarity score and coverage:", c2, cov2
    print "WordSim Relatedness score and coverage:", c3, cov3, "\n"

    print " "
if __name__=='__main__':
    main()

