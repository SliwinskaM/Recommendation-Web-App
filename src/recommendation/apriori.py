import numpy as np
from itertools import combinations, chain, permutations
from scipy.special import comb

class Apriori:
    def __init__(self, conv_r_matrix, sets_enum, min_support=0.2, min_confidence=0.5):
        self.conv_r_matrix = conv_r_matrix
        self.number_of_sets = len(conv_r_matrix[0][0])
        self.number_of_products = len(conv_r_matrix[0])
        self.number_of_users = len(conv_r_matrix)
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.sets_enum = sets_enum
        self.transactions_all_np = np.nonzero(~np.isnan(self.conv_r_matrix[:, :, 0]))

    # "Product" representation: [index of Product, index of Fuzzy Set]
    ProductScore = tuple([int, int])


    def count(self, items):
        count_np = 0
        # indexes of items and scores
        items_nums = np.array(items[:, 0])
        items_scores = np.array(items[:, 1])
        # transactions containing each item individually
        items_in_transactions_mask = np.isin(self.transactions_all_np[1], items_nums)
        # users that bought individual items
        users_for_items = self.transactions_all_np[0][items_in_transactions_mask]
        # users that bought all of the items
        unique, counts = np.unique(users_for_items, return_counts=True)
        users_ok = unique[counts == len(items)]
        if users_ok.size > 0:
            # scores for each user
            rows_scores = self.conv_r_matrix[users_ok][:, items_nums, items_scores]
            counts = np.min(rows_scores, axis=1)
            # final sum
            count_np = sum(counts)
        return count_np

    def support(self, count):
        return count / self.number_of_users


    def confidence(self, itemset_support, pred_support):
        conf_np = itemset_support / pred_support
        return conf_np


    # First candidates - all possibilities
    def create_c_1(self):
        c_1 = np.transpose(np.meshgrid(range(self.number_of_products), self.sets_enum)).reshape((-1, 1, 2))
        return c_1


    # Check candidates' support
    def gen_l_k(self, c_k):
        # support of each candidate
        counts = np.array([self.count(row) for row in c_k])
        # find candidates with proper support
        u = self.support(counts)
        l_k_mask = np.where(self.support(counts) >= self.min_support) # itemsets with proper support
        l_k = c_k[l_k_mask]
        counts_matr = counts[l_k_mask]
        return l_k, counts_matr


    # Helper function - indexes of combinations with given parameters
    def comb_index(self, n, k):
        count = comb(n, k, exact=True)
        index = np.fromiter(chain.from_iterable(combinations(range(n), k)),
                            int, count=count * k)
        return index.reshape(-1, k)

    # Generate candidates
    def gen_c_k(self, l_prev, k):
        # JOINING
        # pairs of indexes of sets to potentially join
        set_pairs_all = np.array(np.meshgrid(range(len(l_prev)), range(len(l_prev)))).T.reshape(-1,2)
        set_pairs = np.unique(np.sort(set_pairs_all,axis=1),axis=0)
        # check conditions
        join_1 = [[True]] * len(set_pairs)
        if k > 2:
            # condition 1 - all elements equal except last
            join_1 = np.all(np.all(np.equal(l_prev[set_pairs[:, 0], :k - 2], l_prev[set_pairs[:, 1], :k - 2]), axis=1), axis=1).reshape(-1,1)
        # condition 2 - last elements not equal
        join_2 = ~(np.equal(l_prev[set_pairs[:,0], k - 2][:,0], l_prev[set_pairs[:,1], k - 2][:,0])).reshape(-1,1)
        # both conditions
        join_np = np.all(np.concatenate((join_1, join_2), axis=1), axis=1)
        # pairs of indexes of sets to join
        to_join = set_pairs[join_np]

        if np.any(to_join):
            # to retain order - item with bigger index goes first
            first_0 = l_prev[to_join[:,0], k - 2][:,0] < l_prev[to_join[:,1], k - 2][:,0]
            first_0 = np.stack((first_0, first_0)).T
            firsts = np.where(first_0, l_prev[to_join[:,0], k - 2], l_prev[to_join[:,1], k - 2])
            seconds = np.where(~first_0, l_prev[to_join[:,0], k - 2], l_prev[to_join[:,1], k - 2])

            # final joining
            if k <= 2:
                candidates = np.array(list(zip(firsts, seconds)))
            else:
                candidates = np.concatenate((l_prev[to_join[:, 0], :k-2], np.expand_dims(firsts, axis=1), np.expand_dims(seconds, axis=1)), axis=-2)
        else:
            candidates = np.array([])

        # PRUNING
        if np.any(to_join):
            # subsets of all sets in candidates
            subsets_idx = self.comb_index(k, k-1)
            subsets = candidates[:, subsets_idx]
            # for every subset - check if it is in l_prev
            l_prev_list = l_prev.tolist()
            subsets_list = subsets.tolist()
            prune_mask = np.ones(len(subsets), dtype=bool)
            for c in range(len(subsets_list)):
                for subset in subsets_list[c]:
                    if subset not in l_prev_list:
                        prune_mask[c] = False
            pass
            # leave only subsets that fulfill the condition
            candidates = candidates[prune_mask]
        return candidates


    # main Apriori
    def apriori(self):
        # first iteration - create matrixes
        # generate first array of candidates
        c = self.create_c_1()
        # generate first array of frequent sets and supports
        l, cnt = self.gen_l_k(c)

        counts_final = [cnt]
        l_final = [l]
        if l.size > 0:
            for k in range(2, self.number_of_products):
                # generate array of candidates
                c = self.gen_c_k(l, k)
                # generate array of frequent sets and supports
                l, cnt = self.gen_l_k(c)
                # if there are no more frequent sets
                if l.size == 0:
                    break
                l_final.append(l)
                counts_final.append(cnt)
        return l_final, counts_final




# -- FOR DEBUGGING --------------------------------------------------------
    # Generate association rules based on frequent itemsets
    def generate_rules(self, frequent_sets, counts):
        rules2 = []
        for itemset_length_idx in range(1, len(frequent_sets)):
            itemset_length = itemset_length_idx + 1
            for itemset_idx in range(len(frequent_sets[itemset_length_idx])):
                itemset = frequent_sets[itemset_length_idx][itemset_idx]
                itemset_support = counts[itemset_length_idx][itemset_idx]
                # generate all possible rules from a set
                for pred_length in range(1, itemset_length):
                    for pred_idx in combinations(range(itemset_length), pred_length):
                        pred = itemset[list(tuple(pred_idx))]
                        pred_support_idx = np.nonzero(np.all(np.all(frequent_sets[pred_length-1] == pred, axis=1), axis=1))
                        pred_support = counts[pred_length - 1][pred_support_idx]
                        desc = np.delete(itemset, pred_idx, 0)
                        # consider only rules leading to the highest score
                        successor_scores = desc[:,1]
                        if np.all(successor_scores == len(self.sets_enum) - 1):
                            # check the confidence
                            conf = self.confidence(itemset_support, pred_support)
                            if conf >= self.min_confidence:
                                rules2.append([pred, desc])
        return rules2


    def algorithm_main(self):
        frequent_sets, supports = self.apriori()
        debug = self.generate_rules(frequent_sets, supports)
        return debug
