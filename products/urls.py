from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    #"""function based views"""
    # path('',product_list, name='Product_list'),
    # path('category/<slug:category_slug>', product_list, name='Category_detail'),
    # path('category/<slug:category_slug>/<slug:product_slug>', product_detail, name='Product_detail'),
    # path('category/<slug:category_slug>/<slug:product_slug>/<int:image_id>', image_detail, name='Image_detail'),
    # path('category/<slug:category_slug>/<slug:product_slug>/create_review', review_form, name='Review_create'),
    # path('category/<slug:category_slug>/<slug:product_slug>/rate', rating_form, name='Rating_create'),


    # """class based views"""
    path('',ProductList.as_view(), name='Product_list'),
    path('category/<slug:category_slug>', ProductList.as_view(), name='Category_detail'),
    path('category/<slug:category_slug>/<slug:product_slug>', ProductDetailView.as_view(), name='Product_detail'),
    path('category/<slug:category_slug>/<slug:product_slug>/create', ReviewCreateView.as_view(), name='Review_create'),
    path('category/<slug:category_slug>/<slug:product_slug>/rate', RatingCreateView.as_view(), name='Rating_create'),
    path('category/<slug:category_slug>/<slug:product_slug>/<int:image_id>', ImageDetailView.as_view(), name='Image_detail'),

]