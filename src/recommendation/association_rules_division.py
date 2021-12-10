import numpy as np
from itertools import combinations
from . import apriori as apr
import math

class AssociationRules:
    def __init__(self, conv_r_matrix, div_percentage, sets_enum, min_support=0.2, min_confidence=0.5):
        self.conv_r_matrix = conv_r_matrix
        self.number_of_users = len(conv_r_matrix)
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.sets_enum = sets_enum
        self.max_div_size = div_percentage * self.number_of_users / 100  # users instead of transactions
        self.r_divisions = []
        self.min_count = self.min_support * self.number_of_users

    # "Product" representation: [index of Product, index of Fuzzy Set]
    ProductScore = np.array([int, int])

    # find maximum level of division and number of divisions
    def division_params(self):
        curr_size = self.number_of_users
        level = 1
        number_of_divisions = 1
        # divide until maximum division size is reached
        while curr_size > self.max_div_size:
            curr_size /= 2
            level += 1
            number_of_divisions *= 2
        return level, number_of_divisions

    # Unite two sub-databases
    def unite(self, min_count, sub_tdb1, sub_tdb2, counts_tdb1, counts_tdb2):
        # sets' lengths in sub_tdb1
        lengths1 = np.array([np.shape(elem)[1] for elem in sub_tdb1])
        # merge both sub-databases
        for length_idx2 in range(len(sub_tdb2)):
            # iterate through freguent sets in sub_tdb2
            for t_idx in range(len(sub_tdb2[length_idx2])):
                # operate on same sets' lengths in both sub-databases
                length_idx1 = np.where(lengths1 == length_idx2 + 1)
                # if matching length in sub_tdb1 found
                if len(length_idx1[0]) > 0:
                    # check if frequent set already exists in sub_tdb1
                    t_in_tdb1 = np.where(np.all(np.all(sub_tdb2[length_idx2][t_idx] == sub_tdb1[length_idx1[0][0]], axis=1), axis=1))
                    # if set already exists in sub_tdb1, increase its support
                    if len(t_in_tdb1[0]) > 0:
                        counts_tdb1[length_idx2][t_in_tdb1] += counts_tdb2[length_idx2][t_idx]
                    # if not, add it to respective length
                    elif counts_tdb2[length_idx2][t_idx] >= min_count:
                        sub_tdb1[length_idx2] = np.append(sub_tdb1[length_idx2], [sub_tdb2[length_idx2][t_idx]], axis=0)
                        counts_tdb1[length_idx2] = np.append(counts_tdb1[length_idx2], [counts_tdb2[length_idx2][t_idx]], axis=0)
                # if matching length not found, add new row to sub_tdb1
                elif counts_tdb2[length_idx2][t_idx] >= min_count:
                    sub_tdb1.append(np.array(np.expand_dims(sub_tdb2[length_idx2][t_idx], axis=0), dtype=object))
                    counts_tdb1.append(np.array([counts_tdb2[length_idx2][t_idx]]))
                    lengths1 = np.append(lengths1, length_idx2+1)

        # check if updated supports match the condition
        for length_idx1 in range(len(sub_tdb1)):
            sup_mask = counts_tdb1[length_idx1] >= min_count
            sub_tdb1[length_idx1] = sub_tdb1[length_idx1][sup_mask]
            counts_tdb1[length_idx1] = counts_tdb1[length_idx1][sup_mask]

        return sub_tdb1, counts_tdb1


    def main(self):
        number_of_levels, number_of_divisions = self.division_params()
        # divide transactional database into parts
        self.r_divisions = np.array_split(self.conv_r_matrix, number_of_divisions)
        frequent_matrix = []
        counts_matrix = []

        # find frequent sets in every division
        for division in self.r_divisions:
            apriori = apr.Apriori(division, self.sets_enum, self.min_support)
            frequent_sets, counts = apriori.apriori()
            frequent_matrix.append(frequent_sets)
            # supports counted in relation to the whole database
            counts_matrix.append(counts)

        # UNITING
        # minimum count needed increases with every level
        for lvl in range(number_of_levels, 0, -1):
            divs_num = int(math.pow(2, lvl - 1))
            curr_min_count = self.min_count / divs_num * 2
            for j in range(int(divs_num / 2)):
                frequent_matrix[j], counts_matrix[j] = self.unite(curr_min_count, frequent_matrix[j*2], frequent_matrix[j*2+1], counts_matrix[j*2], counts_matrix[j*2+1])
        return frequent_matrix[0], counts_matrix[0]


    def confidence(self, itemset_count, pred_count):
        conf_np = itemset_count / pred_count
        return conf_np


    # Generate association rules based on frequent itemsets
    def generate_rules(self, frequent_sets, counts):
        rules = []
        confidences = []
        supports = []

        # for all frequent itemsets
        for itemset_length_idx in range(1, len(frequent_sets)):
            itemset_length = itemset_length_idx + 1
            for itemset_idx in range(len(frequent_sets[itemset_length_idx])):
                itemset = frequent_sets[itemset_length_idx][itemset_idx]
                itemset_count = counts[itemset_length_idx][itemset_idx]
                potential_rules = []
                # generate all possible rules from a set - beginning from these with longest predecessors
                for antec_length in range(itemset_length - 1, 0, -1):
                    for antec_idx in combinations(range(itemset_length), antec_length):
                        # get antecedent and consequent
                        antecedent = itemset[list(tuple(antec_idx))]
                        consequent = np.delete(itemset, antec_idx, 0)
                        potential_rules.append([antecedent, consequent])

                # check the potencial rules
                for pot_rule in potential_rules:
                    antecedent, consequent = pot_rule
                    # get the antecedent's supports
                    antec_count_idx = np.nonzero(
                        np.all(np.all(frequent_sets[len(antecedent) - 1] == antecedent, axis=1), axis=1))
                    # consider only rules leading to the highest score
                    consequent_scores = consequent[:,1]
                    antec_count = counts[len(antecedent) - 1][antec_count_idx]
                    # check the confidence
                    conf = self.confidence(itemset_count, antec_count)
                    if conf >= self.min_confidence:
                        # check if rule leads to the highest score
                        if np.all(consequent_scores == len(self.sets_enum) - 1):
                            #generate rule
                            rules.append(np.array((antecedent, consequent), dtype=object))
                            confidences.append(conf)
                            supports.append(itemset_count / self.number_of_users)
                    # if rule's confidence is too low, its 'children' in the rules tree also can be excluded
                    else:
                        pot_rules_to_delete = []
                        for lower_antec_length in range(len(antecedent) - 1, 0, -1):
                            for lower_antec in combinations(antecedent, lower_antec_length):
                                for pot_rule_del_idx in range(len(potential_rules)):
                                    if np.all(np.all(potential_rules[pot_rule_del_idx][0] == np.array(lower_antec))):
                                        pot_rules_to_delete.append(pot_rule_del_idx)
                        potential_rules = np.delete(potential_rules, pot_rules_to_delete, axis=0)
                        pass

        return rules, confidences, supports


    def algorithm_main(self):
        frequent_sets, counts = self.main()
        return self.generate_rules(frequent_sets, counts)
