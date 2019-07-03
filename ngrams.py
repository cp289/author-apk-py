from bs4 import BeautifulSoup
import os
import settings
from message import *

def get_n_grams(strings):

    dictionary = {}

    for string in strings:

        n_grams = zip(*[string[i:] for i in range(3)])

        for n_gram in n_grams:
            get_occurance(dictionary, n_gram)

    return dictionary


# Takes in the tuple as the key and checks the dictionary to see if it is already in there, and if not, it is added
def get_occurance(dictionary, key):
    if key in dictionary:
        dictionary[key] += 1
    else:
        dictionary[key] = 1

    return dictionary
