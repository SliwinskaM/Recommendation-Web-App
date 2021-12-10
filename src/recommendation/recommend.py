from statistics import mean

import math
import numpy as np
from sklearn.model_selection import train_test_split
from . import association_rules_division as ard
from . import apriori as apr
from . import visualizations as vs

class Recommend:
    def __init__(self, conv_r_matrix):
        self.conv_r_matrix = conv_r_matrix
        self.rules = []

    def recommend_to_user(self, rules, cofidences, supports, matrix, user_idx):
        user_p_s_idxs = np.nonzero(~np.isnan(matrix[user_idx]))
        user_p_s = list(zip(user_p_s_idxs[0], user_p_s_idxs[1]))

        recomm_list = []
        harm_mean_list = []
        recomm_to_harm_mean = {}

        for i in range(len(rules)):
            antec, conseq = rules[i]
            conseq = list(conseq)
            conf = cofidences[i][0]
            supp = supports[i]
            # check if user bought antequant's elements
            antec_in_user = True
            for elem in antec:
                if tuple(elem) not in user_p_s:
                    antec_in_user = False
                # check if user liked the product
                elif matrix[user_idx,elem[0],elem[1]] == 0:
                    antec_in_user = False

            # check if user bought consequent's elements
            conseq_to_delete = []
            for elem_idx in range(len(conseq)):
                if tuple(conseq[elem_idx]) in user_p_s:
                    conseq_to_delete.append(elem_idx)
            conseq = list(np.delete(conseq, conseq_to_delete, axis=0))

            # join both conditions
            if antec_in_user and len(conseq) != 0:
                for elem in conseq:
                    new_recomm = elem[0]
                    harm_mean = 2 * conf * supp / (conf + supp)
                    # if product already recommended
                    if new_recomm in recomm_list:
                        recomm_idx = recomm_list.index(new_recomm)
                        harm_mean_list[recomm_idx] += harm_mean
                        pass
                    else:
                        recomm_list.append(new_recomm)
                        harm_mean_list.append(harm_mean)
                        pass
        return recomm_list, harm_mean_list

    # calculate  AP@N for user
    def ap_n_user(self, n, all_len, is_relevant_list, precision_k_list):
        helper_sum = 0
        for k in range(n):
            if k < len(is_relevant_list):
                helper_sum += precision_k_list[k] * is_relevant_list[k]
        ap_n_user = (1 / all_len) * helper_sum
        return ap_n_user


    # create and validate recommendations
    def main_recommend(self, S, curves_names, test_size=0.3, cross_num=10, min_support=0.2, min_confidence=0.5, shuffle_test=False):
        # initialize
        train_idxs, test_idxs = train_test_split(range(len(self.conv_r_matrix)), test_size=test_size, shuffle=shuffle_test)
        train = self.conv_r_matrix[train_idxs]
        test = self.conv_r_matrix[test_idxs]

        apriori = ard.AssociationRules(train, S, curves_names, min_support, min_confidence)
        rules, confidences, supports = apriori.algorithm_main()
        print('Rules found')
        self.rules = rules
        # all recommendations
        recommendations_all = {}
        precision_all = []
        map_3_list = []
        map_5_list = []
        map_7_list = []
        map_10_list = []
        map_20_list = []


        # cross-validate recommendations on test matrix
        for i_cross in range(cross_num):
            ap_3_user_dict = {}
            ap_5_user_dict = {}
            ap_7_user_dict = {}
            ap_10_user_dict = {}
            ap_20_user_dict = {}

            print('cross ' + str(i_cross))
            # initialize cross validation cross base and cross test
            cross_base = np.empty(test.shape)
            cross_base[:] = np.nan
            cross_test = np.empty(test.shape)
            cross_test[:] = np.nan

            cross_part_size = math.floor(train.shape[1] / cross_num)
            if i_cross < cross_num-1:
                cross_test_range = range((i_cross * cross_part_size), ((i_cross + 1) * cross_part_size))
                cross_test[:, cross_test_range] = test[:, cross_test_range]
                cross_base[:, :(i_cross * cross_part_size)] = test[:, :(i_cross * cross_part_size)]
                cross_base[:, ((i_cross + 1) * cross_part_size):] = test[:, ((i_cross + 1) * cross_part_size):]
            else:
                cross_test[:, (i_cross * cross_part_size):] = test[:, (i_cross * cross_part_size):]
                cross_base[:, :(i_cross * cross_part_size)] = test[:, :(i_cross * cross_part_size)]


                # recommend products to every user and check if they have really bought it
            for test_user_idx in range(len(test)):
                # recommendations based on cross base sorted by their harmonic means
                recommendations_unsorted, harm_means_unsorted = self.recommend_to_user(rules, confidences, supports, cross_base, test_user_idx)
                sorting_helper = sorted(zip(harm_means_unsorted, range(len(harm_means_unsorted))))
                harm_means = [h for h,_ in sorting_helper]
                sort_idxs = [i for _,i in sorting_helper]
                recommendations = [recommendations_unsorted[i_s] for i_s in sort_idxs]

                # other products bought by user (cross test)
                cross_test_p_s_idxs = np.nonzero(~np.isnan(cross_test[test_user_idx]))

                #debug
                debug_user_test = test[test_user_idx]
                debug_user_r_matrix = self.conv_r_matrix[test_idxs[test_user_idx]]
                debug_cond = np.all([np.where(~np.isnan(debug_user_test))[i] == np.where(~np.isnan(debug_user_r_matrix))[i] for i in range(len(np.where(~np.isnan(debug_user_test))))])
                if not debug_cond:
                    print('ALERT')

                # count precise recommendations
                # if user bought any products belonging to cross test:
                if len(cross_test_p_s_idxs[0]) > 0:
                    recommendations_all[test_idxs[test_user_idx]] = recommendations
                    # calculate precision of recommendation of every product
                    relevant_recommendations = 0
                    current_number_of_recommendations = 0
                    precision_k_list = []
                    is_relevant_list = []
                    for prod in recommendations:
                        current_number_of_recommendations += 1
                        #if prod is in cross_test, add its fuzzy function for HIGH to recommendation counter
                        if prod in cross_test_p_s_idxs[0]:
                            prod_high_score = self.conv_r_matrix[test_idxs[test_user_idx], prod, len(curves_names) - 1]
                            # decide whether recommendation is relevant:
                            if prod_high_score > 0:
                                relevant_recommendations += prod_high_score
                                is_relevant_list.append(True)
                            else:
                                is_relevant_list.append(False)
                        else:
                            is_relevant_list.append(False)
                        precision_k = relevant_recommendations / current_number_of_recommendations
                        precision_k_list.append(precision_k)

                    if len(recommendations) > 0:
                        # calculate different AP@N for user
                        ap_3_user_dict[test_idxs[test_user_idx]] = self.ap_n_user(3, len(recommendations), is_relevant_list, precision_k_list)
                        ap_5_user_dict[test_idxs[test_user_idx]] = self.ap_n_user(5, len(recommendations),
                                                                                  is_relevant_list, precision_k_list)
                        ap_7_user_dict[test_idxs[test_user_idx]] = self.ap_n_user(7, len(recommendations),
                                                                                  is_relevant_list, precision_k_list)
                        ap_10_user_dict[test_idxs[test_user_idx]] = self.ap_n_user(10, len(recommendations),
                                                                                   is_relevant_list, precision_k_list)
                        ap_20_user_dict[test_idxs[test_user_idx]] = self.ap_n_user(20, len(recommendations),
                                                                                   is_relevant_list, precision_k_list)

            # calculate collective precision
            map_3_all = 0
            map_5_all = 0
            map_7_all = 0
            map_10_all = 0
            map_20_all = 0
            if len(ap_3_user_dict.values()) > 0:
                map_3_all = round(mean(ap_3_user_dict.values()), 5)
            if len(ap_5_user_dict.values()) > 0:
                map_5_all = round(mean(ap_5_user_dict.values()), 5)
            if len(ap_7_user_dict.values()) > 0:
                map_7_all = round(mean(ap_7_user_dict.values()), 5)
            if len(ap_10_user_dict.values()) > 0:
                map_10_all = round(mean(ap_10_user_dict.values()), 5)
            if len(ap_20_user_dict.values()) > 0:
                map_20_all = round(mean(ap_20_user_dict.values()), 5)
            map_3_list.append(map_3_all)
            map_5_list.append(map_5_all)
            map_7_list.append(map_7_all)
            map_10_list.append(map_10_all)
            map_20_list.append(map_20_all)
        return recommendations_all, map_3_list, map_5_list, map_7_list, map_10_list, map_20_list
