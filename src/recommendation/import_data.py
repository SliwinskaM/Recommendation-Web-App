from statistics import mean
import numpy as np
import pandas as pd
import csv

from products.models import Product
from ratings.models import Rating
from django.contrib.auth.models import User



class ImportData:
    def __init__(self, dataset):
        self.dataset = dataset
        self.r_matrix = []  # R matrix (users x products, elements: ratings)
        self.t_matrix = []  # T matrix (users x products, elements: timestamps)
        self.users = np.array([], dtype=str)  # already searched users
        self.products = np.array([], dtype=str)  # already searched products
        self.min_score = 0
        self.max_score = 0

    class Parameters:
        def __init__(self, filename, min_score, max_score, user_column, product_column, score_column,
                     time_column=None, parse_date=0, read_time=True, args=None):
            self.filename = filename
            self.min_score = min_score
            self.max_score = max_score
            self.user_column = user_column
            self.product_column = product_column
            self.score_column = score_column
            self.time_column = time_column
            self.parse_date = parse_date
            self.read_time = read_time
            self.args = args

    params_dict = {
        'beauty': Parameters('Datasets/RatingBeautyShort.csv', 1, 5, 'UserId', 'ProductId', 'Rating',
                                    'Timestamp'),
        'electronics': Parameters('Datasets/ElectronicsShort.csv', 1, 5, 0, 1, 2, 3),
        'smoker': Parameters('recommendation/Datasets/smokerdata3.csv', 1, 5, 'User', 'Brand', 'Rating', read_time=False),
        'movies': Parameters('Datasets', 0.5, 5, 'userId', 'movieId', 'rating', 'timestamp', read_time=False),
    }

    def add_rating(self, user, product, score):
        with open('recommendation/Datasets/smokerdata3.csv', 'a') as fd:
            fd.write(user + ',' + product + ',' + 'none,none,none,none,none,none,' + str(score) + '\n')

        if Rating.objects.filter(user=user).filter(product=product):
            rating = Rating.objects.filter(user=user).filter(product=product)[0]
            rating.score = score
            rating.save()
        else:
            Rating.objects.create(
                **{'user': user, 'product': product, 'score': score, 'shop': 'smokers'})

        # if user not in self.users:
        #     self.users = np.append(self.users, str(user))
        #     self.r_matrix = np.append(self.r_matrix, [[np.nan for i in range(len(self.r_matrix[0]))]], axis=0)

        # add to django database
        # if not User.objects.filter(username=str(user)):
        #     User.objects.create_user(user, password='pass')

        # if product not in self.products:  # to avoid repetition
        #     self.products = np.append(self.products, str(product))
        #     self.r_matrix = np.append(self.r_matrix, np.transpose([[np.nan for i in range(len(self.r_matrix))]]), axis=1)
        #     find_user = np.where(self.users == user)
        #     self.r_matrix[find_user, -1] = rating
        # else:
        # find_user = np.where(self.users == user)[0]
        # find_prod = np.where(self.products == product)[0]
        # self.r_matrix[find_user, find_prod] = rating

        # # add to django database
        # if not Product.objects.filter(name=str(product)):
        #     Product.objects.create(**{'idx': len(self.r_matrix[0]), 'name': product, 'shop_name': self.dataset})




    def import_data(self):
        params = self.params_dict[self.dataset]
        # create database
        if params.read_time:
            df = pd.read_csv(params.filename,
                             usecols=[params.user_column, params.product_column, params.score_column, params.time_column])
        else:
            df = pd.read_csv(params.filename,
                             usecols=[params.user_column, params.product_column, params.score_column])
        self.min_score = params.min_score
        self.max_score = params.max_score
        # initialize lists
        user_max_idx = -1
        prod_max_idx = -1
        r_matrix = []
        users = []
        products = []
        # Write to lists
        for index, row in df.iterrows():
            user = row[params.user_column]
            product = row[params.product_column]

            if user not in users:
                user_max_idx += 1
                users.append(user)
                r_matrix.append([np.nan for i in range(prod_max_idx + 1)])

            # add to django database
            if not User.objects.filter(username=user):
                # print(user)
                User.objects.create_user(user, password='pass')

            if product not in products:  # to avoid repetition
                prod_max_idx += 1
                products.append(product)
                for i in range(len(r_matrix)):
                    r_matrix[i].append(np.nan)
                find_user = users.index(user)
                r_matrix[find_user][prod_max_idx] = row[params.score_column]
            else:
                find_prod = products.index(product)
                find_user = users.index(user)
                r_matrix[find_user][find_prod] = row[params.score_column]

            # add to django database
            if not Product.objects.filter(name=product):
                Product.objects.create(**{'idx': prod_max_idx, 'name': product, 'shop_name': self.dataset})

            if Rating.objects.filter(user=user).filter(product=product):
                rating = Rating.objects.filter(user=user).filter(product=product)[0]
                rating.score = row[params.score_column]
                rating.save()
            else:
                Rating.objects.create(**{'user': user, 'product': product, 'score': row[params.score_column], 'shop': 'smokers'})

        self.users = np.array(users)
        self.products = np.array(products)
        self.r_matrix = np.array(r_matrix, dtype=object)
        print('Data imported')


    def import_movies_genres(self):
        params = self.params_dict[self.dataset]
        # create helper database
        types = pd.read_csv(params.filename + '/TypesMovies.csv', usecols=['movieId', 'genres'])
        # create database
        if params.read_time:
            df = pd.read_csv(params.filename + '/RatingMovies.csv',
                             usecols=[params.user_column, params.product_column, params.score_column, params.time_column])
        else:
            df = pd.read_csv(params.filename + '/RatingMovies.csv',
                             usecols=[params.user_column, params.product_column, params.score_column])
        self.min_score = params.min_score
        self.max_score = params.max_score
        # initialize lists
        user_max_idx = -1
        genre_max_idx = -1
        r_matrix = []
        t_matrix = []
        users = []
        genres = []
        # helper matrices
        movie_id_to_genres = {}
        for index, row in types.iterrows():
            movie_id = row['movieId']
            genres_row = row['genres']
            genres_list = genres_row.split('|')
            movie_id_to_genres[movie_id] = genres_list

        # Write to lists
        for index, row in df.iterrows():
            user = row[params.user_column]
            product = row[params.product_column]
            if user not in users:
                user_max_idx += 1
                users.append(user)
                r_matrix.append([[] for i in range(genre_max_idx + 1)])
            for genre in movie_id_to_genres[product]:
                if genre not in genres:  # to avoid repetition
                    genre_max_idx += 1
                    genres.append(genre)
                    for i in range(len(r_matrix)):
                        r_matrix[i].append([])
                    r_matrix[user_max_idx][genre_max_idx].append(row[params.score_column])
                else:
                    find_genre = genres.index(genre)
                    r_matrix[user_max_idx][find_genre].append(row[params.score_column])

        for row in range(len(r_matrix)):
            for col in range(len(r_matrix[0])):
                if len(r_matrix[row][col]) > 0:
                    r_matrix[row][col] = mean(r_matrix[row][col])
                else:
                    r_matrix[row][col] = np.nan


        self.users = np.array(users)
        self.products = np.array(genres)
        self.r_matrix = np.array(r_matrix, dtype=object)
        print('Data imported')
