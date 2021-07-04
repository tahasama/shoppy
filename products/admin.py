from django.contrib import admin
from django.db.models.aggregates import Avg
from.models import Category, Product, Image, Review, Rating

admin.site.register(Review)

admin.site.register(Rating)


admin.site.register(Category)

class Imageline(admin.StackedInline):
    model = Image

class Reviewline(admin.StackedInline):
    model = Review  

class Ratingline(admin.StackedInline):
    model = Rating    

class ProductAdmin(admin.ModelAdmin):
    inlines = [Imageline, Reviewline, Ratingline,]

admin.site.register(Product, ProductAdmin)