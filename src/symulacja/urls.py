"""symulacja URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.contrib.auth import views as auth_views

from pages.views import home_view
from products.views import ProductListView, ProductDetailView, ProductCreateView, ProductDeleteView
from recommendation.views import shop_add_view, recommendation_list_view
from ratings.views import rating_create_view, RatingListView, rating_product_view

# from users.views import UserListView, UserDetailView, UserCreateView, UserUpdateView, UserDeleteView

urlpatterns = [
    path('', auth_views.LoginView.as_view(), name='login'),

    path('home/', home_view, name='home'),

    path('admin/', admin.site.urls),

    path('product/list/', ProductListView.as_view(), name='product_list'),
    path('product/<int:id>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/delete/<int:id>/', ProductDeleteView.as_view(), name='product_delete'),

    path('shop/add/', shop_add_view, name='add_shop'),

    path('recommendation/list/', recommendation_list_view, name='recommendation_list'),

    path('rating/create/', rating_create_view, name='rating_create'),
    path('rating/create/<int:p_id>/', rating_product_view, name='rating_product'),
    path('rating/list/', RatingListView.as_view(), name='rating_list')
]
