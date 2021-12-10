from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import numpy as np

from . import import_data
from . import apriori as apr
from . import association_rules_division as ard
from .additional_functions import create_converted_r_matrix
from . import fuzzy_curves as fc
from . import recommend as re
from . import visualizations as vs

from .models import Recommendation
from products.models import Product

# Create your views here.


@login_required
def shop_add_view(request, *args, **kwargs):
    data = import_data.ImportData('smoker')
    data.import_data()
    return render(request, "shops/shop_add.html", {})


@login_required
def recommendation_list_view(request, *args, **kwargs):
    # all products
    all_products = Product.objects.all()

    # recommend
    count_recommendations_user(request.user)
    recomm_queryset = Recommendation.objects.filter(username=request.user)
    recomms = []
    if recomm_queryset:
        # recomm_queryset = Recommendation.objects.filter(username=request.user)[0]
        recomm_idx_list_str = recomm_queryset[0].products[1:-1].split(", ")
        recomm_idx_list = [int(item) for item in recomm_idx_list_str]
        for recomm_number in recomm_idx_list:
            product = Product.objects.get(idx=recomm_number)
            recomms.append(product)
    context = {
        'queryset': recomm_queryset,
        'recomm_list': recomms,
        'all_products': all_products
    }
    return render(request, "recommendation/recommendation_list.html", context)


# additional functions
def count_recommendations_user(username):
    data = import_data.ImportData('smoker')
    data.import_data()
    # choose fuzzy curves class
    curves = fc.Curves1(data.min_score, data.max_score, 0.2, 0.45, 0.55, 0.8)
    # create fuzzy association rules
    conv_r_matrix = create_converted_r_matrix(data.r_matrix, curves)
    print('Got conv_r_matrix')
    # generate association rules
    association = ard.AssociationRules(conv_r_matrix, 20, curves.Names, min_support=0.002, min_confidence=0.01)
    rules, confidences, supports = association.algorithm_main()
    print('Rules found: ', len(rules))
    # recommend products to users
    usr_idx = np.where(data.users == str(username))[0][0] # find user index in matrix
    recomm = re.Recommend(conv_r_matrix)
    recomm_list, harm_mean_list = recomm.recommend_to_user(rules, confidences, supports, conv_r_matrix, usr_idx)
    print('Recommendations found: ', recomm_list)

    # update object in database
    is_user = Recommendation.objects.filter(username=str(username))
    if is_user:
        recommendation = Recommendation.objects.get(username=str(username))
        recommendation.products = str(recomm_list)
        recommendation.save()
    else:
        recommendation = Recommendation(username=str(username), products=str(recomm_list), shop='smokers')
        recommendation.save()


def create_recommendations_all():
    data = import_data.ImportData('smoker')
    data.import_data()
    # choose fuzzy curves class
    curves = fc.Curves1(data.min_score, data.max_score, 0.2, 0.45, 0.55, 0.8)
    # create fuzzy association rules
    conv_r_matrix = create_converted_r_matrix(data.r_matrix, curves)
    # generate association rules
    association = ard.AssociationRules(conv_r_matrix, 20, curves.Names, min_support=0.002, min_confidence=0.01)
    rules, confidences, supports = association.algorithm_main()

    # recommend products to users
    all_users = User.objects.all()
    for user in all_users.iterator():
        username = user.username
        usr_idx = np.where(data.users == username) # find user index in matrix
        recomm = re.Recommend(conv_r_matrix)
        recomm_list, harm_mean_list = recomm.recommend_to_user(rules, confidences, supports, conv_r_matrix, usr_idx)

        # update object in database
        is_user = Recommendation.objects.filter(username=str(username))
        if is_user:
            recommendation = Recommendation.objects.get(username=str(username))
            recommendation.products = str(recomm_list)
            recommendation.save()
        else:
            recommendation = Recommendation(username=str(username), products=str(recomm_list), shop='smokers')
            recommendation.save()