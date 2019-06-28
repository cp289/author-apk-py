from bs4 import BeautifulSoup
import os
import settings
import message

def get_n_grams(self, path):

    dictionary = {}

    xml_path = os.path.join(self.dir, path)

    with open(xml_path) as xml_file:
        parser = BeautifulSoup(xml_file, features="lxml-xml")

    strings = parser.findAll("string")

    for string in strings:

        numbers = bytes(string.text, encoding='utf-8')
        encoded = bytearray(numbers)

        n_grams = zip(*[encoded[i:] for i in range(3)])

        all_n_grams = [" ".join(str(ngram) for ngram in n_grams)]

        for ngram in all_ngrams:
            get_occurance(dictionary, ngram)

        self.n_grams += n_grams


def get_occurance(dictionary, temp):
    if temp in dictionary:
        dictionary[temp] += 1
    else:
        dictionary[temp] = 1

    return dictionary