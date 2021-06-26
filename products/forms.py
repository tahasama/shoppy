from django import forms
from django.forms import models
from django.forms.models import ModelForm
from .models import Category, Product, Image, Review, Rating


class ReviewForm(models.ModelForm):
    class Meta:
        model = Review
        fields = ['comment',]

class RatingForm(models.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating',]
       

                  
    