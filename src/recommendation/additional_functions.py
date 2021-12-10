import numpy as np
from math import isnan
from . import fuzzy_curves

# Create a matrix with fuzzy values for every transaction
def create_converted_r_matrix(prev_r_matrix, curves: fuzzy_curves.FuzzyCurves):
    number_of_sets = curves.get_number_of_sets()
    conv_r_matrix = np.empty([len(prev_r_matrix), len(prev_r_matrix[0]), number_of_sets])
    conv_r_matrix[:] = np.nan
    for user_idx in range(len(conv_r_matrix)):
        for prod_idx in range(len(conv_r_matrix[0])):
            score = prev_r_matrix[user_idx][prod_idx]
            if not isnan(score):
                # changeable number of sets
                for i in range(number_of_sets):
                    fuzzy_curve = curves.get_list_of_curves()[i]
                    conv_r_matrix[user_idx][prod_idx][i] = fuzzy_curve(score)
    return conv_r_matrix
