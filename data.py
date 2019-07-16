#!/usr/bin/python3
#
# data.py: library for data structures
#

# The functions below are for updating occurances in a dictionary
# dict format: { object : n } where n is the number of occurences of object

# Get total occurrences from arbitrary number of dictionaries
def totalOccurrences(*dicts, total={}):
    for d in dicts:
        updateOccurrences(total, d)
    return total

# Add number of occurrences from new dictionary to a running total dictionary
def updateOccurrences(total, new):
    for n in new:
        if n in total:
            total[n] += new[n]
        else:
            total[n] = new[n]
    return total

# Data type for feature vector
class FeatureVector:

    # Number of ngrams
    n_ngrams = 5
    labels = (
        'n_direct_methods',
        'n_virtual_methods',
        'n_abstract_direct_methods',
        'n_abstract_virtual_methods',
        'n_error_handling_methods',
        'n_total_static_fields',
        'n_total_instance_fields',
        'n_total_final_static_fields',
        'n_total_final_instance_fields',
        'n_total_unary_operators',
        'n_total_binary_operators',
        'n_total_immediate_constants',
        *('ngram_%d' % (i) for i in range(n_ngrams))
    )

    # Entries of the feature vector
    n_direct_methods = 0
    n_virtual_methods = 0
    n_abstract_direct_methods = 0
    n_abstract_virtual_methods = 0
    n_error_handling_methods = 0
    n_total_static_fields = 0
    n_total_instance_fields = 0
    n_total_final_static_fields = 0
    n_total_final_instance_fields = 0
    n_total_unary_operators = 0
    n_total_binary_operators = 0
    n_total_immediate_constants = 0
    top_ngrams = ()

    def __init__(self, n_ngrams=5):

        self.n_ngrams = n_ngrams

        # Numeric vector data
        self.vector = ()

    # Generate and return numeric vector
    def get(self):

        self.vector = (
            self.n_direct_methods,
            self.n_virtual_methods,
            self.n_abstract_direct_methods,
            self.n_abstract_virtual_methods,
            self.n_error_handling_methods,
            self.n_total_static_fields,
            self.n_total_instance_fields,
            self.n_total_final_static_fields,
            self.n_total_final_instance_fields,
            self.n_total_unary_operators,
            self.n_total_binary_operators,
            self.n_total_immediate_constants,
            *self.top_ngrams,
        )

        return self.vector

    # Generate and return vector as dictionary
    def getLabeled(self):
        #self.labeled_vector = {
        #    'n_direct_methods' : self.n_direct_methods,
        #    'n_virtual_methods' : self.n_virtual_methods,
        #    'n_abstract_direct_methods' : self.n_abstract_direct_methods,
        #    'n_abstract_virtual_methods' : self.n_abstract_virtual_methods,
        #    'n_error_handling_methods' : self.n_error_handling_methods,
        #    'n_total_static_fields' : self.n_total_static_fields,
        #    'n_total_instance_fields' : self.n_total_instance_fields,
        #    'n_total_final_static_fields' : self.n_total_final_static_fields,
        #    'n_total_final_instance_fields' : self.n_total_final_instance_fields,
        #    'n_total_unary_operators' : self.n_total_unary_operators,
        #    'n_total_binary_operators' : self.n_total_binary_operators,
        #    'n_total_immediate_constants' : self.n_total_immediate_constants,
        #}
        #for i in range(len(self.top_ngrams)):
        #    self.labeled_vector['ngram_%d'%(i)] = self.top_ngrams[i]

        self.labeled_vector = { name:val for name,val in zip(self.labels, self.get()) }
        return self.labeled_vector

    # Nice string representation
    def __repr__(self):
        return format(self.getLabeled())

