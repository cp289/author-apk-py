#!/usr/bin/python3
#
# data.py: library for data structures
#

class heapCounter(object):

    # Simple object to store a data element and the number of occurrences
    class item:
        def __init__(self, data, num):
            self.data = data
            self.num = num

    def __init__(self):

        self.data = []

    # Add element to heap
    def push(self, item):

        pass

    # Pop element off of heap
    def pop(self):

        return None

# Data type for feature vector
class FeatureVector(object):

    def __init__(self):

        self.n_direct_methods = 0           # Number of direct methods
        self.n_virtual_methods = 0          # Number of virtual methods
        self.n_static_fields = 0            # Number of static fields
        self.n_instance_fields = 0          # Number of instance fields
        self.n_abstract_direct_methods = 0  # Number of abstract direct methods
        self.n_abstract_virtual_methods = 0 # Number of abstract virtual methods
        self.n_error_handling_methods = 0   # Number of methods with error handling
        self.n_final_static_fields = 0      # Number of final static fields
        self.n_final_instance_fields = 0    # Number of final instance fields

        self.vector = None  # Numeric vector data
        self.dict = None    # Dictionary data

    # Generate and return numeric vector
    def get(self):

        self.vector = (
            self.n_direct_methods,
            self.n_virtual_methods,
            self.n_static_fields,
            self.n_instance_fields,
            self.n_abstract_direct_methods,
            self.n_abstract_virtual_methods,
            self.n_error_handling_methods,
            self.n_final_static_fields,
            self.n_final_instance_fields,
        )

        return self.vector

    # Nice string representation
    def __repr__(self):

        dict = {
            'n_direct_methods' : self.n_direct_methods,
            'n_virtual_methods' : self.n_virtual_methods,
            'n_static_fields' : self.n_static_fields,
            'n_instance_fields' : self.n_instance_fields,
            'n_abstract_direct_methods' : self.n_abstract_direct_methods,
            'n_abstract_virtual_methods' : self.n_abstract_virtual_methods,
            'n_error_handling_methods' : self.n_error_handling_methods,
            'n_final_static_fields' : self.n_final_static_fields,
            'n_final_instance_fields' : self.n_final_instance_fields,
        }

        return format(dict)

