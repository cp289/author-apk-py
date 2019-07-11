from bs4 import BeautifulSoup
import os
import settings
from message import *

def get_n_grams(strings, n=3):

    dictionary = {}

    for string in strings:
        for i in range(len(string)-n):
            get_occurance(dictionary, string[i:i+n])

    return dictionary


# Takes in the tuple as the key and checks the dictionary to see if it is already in there, and if not, it is added
def get_occurance(dictionary, key):
    if key in dictionary:
        dictionary[key] += 1
    else:
        dictionary[key] = 1

    return dictionary
