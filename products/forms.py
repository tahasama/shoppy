from django import forms
from django.forms import models
from django.forms.models import ModelForm
from django.forms.widgets import Textarea
from .models import Category, Product, Image, Review, Rating


class ReviewForm(forms.ModelForm):
    comment = forms.CharField(label="",widget=forms.Textarea(attrs={'rows':3, 'cols':80, 'placeholder':'write your review here!'}))
    class Meta:
        model = Review
        fields = ['comment',]



class RatingForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=0,max_value=10)
    class Meta:
        model = Rating
        fields = ['rating',]
       

                  
    