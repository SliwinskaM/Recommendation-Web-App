from . import import_data
from . import apriori as apr
from . import association_rules_division as ard
from additional_functions import create_converted_r_matrix
from . import fuzzy_curves as fc
from . import recommend as re
from . import visualizations as vs
from . import numpy as np

# read data
data = import_data.ImportData('smoker')
data.import_data() # for every database except Movies
# data.import_movies_genres() # for Movies

# choose fuzzy curves class
curves = fc.Curves1(data.min_score, data.max_score, 0.2, 0.45, 0.55, 0.8)

# create fuzzy association rules
conv_r_matrix = create_converted_r_matrix(data.r_matrix, curves)

# optional - generate association rules
association = ard.AssociationRules(conv_r_matrix, 20, curves.Names, min_support=0.002, min_confidence=0.01)
rules, confidences, supports = association.algorithm_main()

# optional - validate recommendation algorithm
# recomm = re.Recommend(conv_r_matrix)
# recomm_score, map_3, map_5, map_7, map_10, map_20 = recomm.main_recommend(20, curves.Names, test_size=0.3, cross_num=10, min_support=0.3, min_confidence=0.15)


# optional - recommend products to users
usr_idx = 0
recomm = re.Recommend(conv_r_matrix)
recomm_list, harm_mean_list = recomm.recommend_to_user(rules, confidences, supports, conv_r_matrix, usr_idx)
print(recomm_list)