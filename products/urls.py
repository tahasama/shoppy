from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    #"""function based views"""
    # path('',product_list, name='Product_list'),
    # path('category/<slug:category_slug>/', product_list, name='Category_detail'),
    # path('category/<slug:category_slug>/<slug:product_slug>/', create_review, name='Product_detail'),
    # path('category/<slug:category_slug>/<slug:product_slug>/<int:image_id>/', image_detail, name='Image_detail'),
    # #path('category/<slug:category_slug>/<slug:product_slug>/rate/', create_rating, name='Create_rating'),
    # #path('category/<slug:category_slug>/<slug:product_slug>/create_review/', create_review, name='Create_review'),
    # path('category/<slug:category_slug>/<slug:product_slug>/update_review/<int:review_id>/', update_review, name='Update_review'),
    # path('category/<slug:category_slug>/<slug:product_slug>/delete_review/<int:review_id>/', delete_review, name='Delete_review'),




    # # """class based views"""
    path('',ProductList.as_view(), name='Product_list'),
    path('category/<slug:category_slug>', ProductList.as_view(), name='Category_detail'),
    path('category/<slug:category_slug>/<slug:product_slug>', ProductPage.as_view(), name='Product_detail'),
    # path('category/<slug:category_slug>/<slug:product_slug>/create/', ReviewCreateView.as_view(), name='Review_create'),
    # path('category/<slug:category_slug>/<slug:product_slug>/rate/', RatingCreateView.as_view(), name='Rating_create'),
    path('category/<slug:category_slug>/<slug:product_slug>/<int:image_id>', ImageDetailView.as_view(), name='Image_detail'),
    path('category/<slug:category_slug>/<slug:product_slug>/update_review/<int:review_id>/', ReviewUpdateView.as_view(), name='Update_review'),
    path('category/<slug:category_slug>/<slug:product_slug>/delete_review/<int:review_id>/', ReviewDeleteView.as_view(), name='Delete_review'),

]