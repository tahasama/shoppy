from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import slug_re
from django.db.models.aggregates import Avg, Count
from django.http import request
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.contrib import messages

from .models import Category, Product, Image, Rating, Review
from .forms import ReviewForm, RatingForm


"""Function Based Views"""

# def product_list(request, category_slug=None):
#     """return the whole list of existing products, can be filtered by category,research option, and paginated"""
#     images = Image.objects.all()
#     category = None # initialize to avoid "local variable 'category' referenced before assignment" error
#     name = request.GET.get('name','') # get name from html input, '' to avoid empty error
#     products = Product.objects.filter(available=True, name__icontains=name) # get all available product, stock > 0
#     if category_slug:
#         category = get_object_or_404(Category,slug=category_slug)
#         products = products.filter(category=category).order_by('-id')


#     paginator = Paginator(products, 4) # 4 posts in each page

#     page_number = request.GET.get('page')

#     try:
#         products = paginator.get_page(page_number)
#     except PageNotAnInteger:
#         # If page is not an integer deliver the first page
#         page_obj = paginator.get_page(1)
#     except EmptyPage:
#         # If page is out of range deliver last page of results
#         page_obj = paginator.get_page(paginator.num_pages)

#     return render(request,'list.html',{'category': category,'products': products,'images':images,'page_obj':products})

# def product_detail(request,category_slug,product_slug):
#     product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
#     images = product.images.all() # display images with reverse raltion
#     reviews = Review.objects.filter(product=product)
#     rating = Rating.objects.filter(product=product)
#     print(rating)
#     average_rating = rating.aggregate(avg_rate=Avg('rating'))
#     product.rating=average_rating['avg_rate'] # assign calculated average to general rating of product
#     product.save()
#     return render(request,'detail.html',{'product': product,'reviews':reviews,'images':images, 'rating':rating})

# def image_detail(request,category_slug,product_slug,image_id):
#     """"show evry image as it reel size"""
#     image = get_object_or_404(Image,product__category__slug=category_slug, product__slug=product_slug,id=image_id)
#     return render(request,'image.html',{'image':image})

# def review_form(request,category_slug, product_slug):
#     product = Product.objects.get(category__slug=category_slug, slug=product_slug)
#     user = request.user
#     if request.method == 'POST' and user.is_authenticated:
#             review_form = ReviewForm(data=request.POST)
#             if review_form.is_valid():
#                 review_form = review_form.save(commit=False)
#                 review_form.product = product # store product into the form
#                 review_form.user = user    # store user into the form
#                 review_form.save()
#                 return redirect('Product_detail',category_slug=category_slug, product_slug=product_slug)
#     else:
#         review_form = ReviewForm()
#     return render(request, 'review_form.html', {'review_form':review_form})

# def rating_form(request,category_slug, product_slug):
#     product = Product.objects.get(category__slug=category_slug, slug=product_slug)
#     user = request.user
#     raters = [x.user for x in Rating.objects.filter(product=product)]
#     if user in raters:
#         messages.info(request, 'you already rated this product')
#         return redirect('Product_detail',category_slug=category_slug, product_slug=product_slug)
#     else:
#         if request.method == 'POST':
#                 rating_form = RatingForm(data=request.POST)
#                 if rating_form.is_valid():
#                     rating_form = rating_form.save(commit=False)
#                     rating_form.product = product
#                     rating_form.user = user    
#                     rating_form.save()
#                     return redirect('Product_detail',category_slug=category_slug, product_slug=product_slug)
#         else:
#             rating_form = RatingForm()
#     return render(request, 'rating_form.html', {'rating_form':rating_form})



"""Classed Based Views"""



class ProductList(ListView):
    """return the whole list of existing products, can be filtered by category,research option, and paginated"""
    model = Product
    context_object_name = 'products' # context used in templates
    template_name = 'list.html'
    paginate_by = 4

    def get_queryset(self, *args, **kwargs):
        name = self.request.GET.get('name','') # get name from html input, '' to avoid empty error
        qs = super().get_queryset().filter(available=True, name__icontains=name) # main queryset, with search
        slug = self.kwargs.get('category_slug', None) # get the slug from url, or None(to avoid error if no slug was selected)
        if slug != None:
            return qs.filter(category__slug=slug) # get slug of category through foreignkey relation
        return qs

class ProductDetailView(DetailView):
    """get product detail, and ratings """
    model = Product
    template_name = "detail.html"
    slug_url_kwarg = 'product_slug' # to allow looking by slug instead of default pk, id

    def get_avg(self):
        """independant method to get average rating and keep get method cleaner"""
        self.object = self.get_object() # re-calling a method cause inaccuaracy, un-updated values
        average_rating = Rating.objects.filter(product=self.object).aggregate(avg_rate=Avg('rating'))
        self.object.rating=average_rating['avg_rate'] # assign calculated average to general rating of product
        self.object.save()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["images"] = self.object.images.all() # display images with reverse raltion
        context["reviews"] = self.object.review_products.all() # display images with reverse raltion
        return context
    

    def get(self, request, *args, **kwargs):
            self.get_avg() # call custom fuction so it gets executed when GET call
            return super(ProductDetailView, self).get(request, *args, **kwargs)

class ImageDetailView(DetailView):
    """"show evry image as it reel size"""
    model = Image
    template_name = "image.html"
    context_object_name = "image"
    pk_url_kwarg = "image_id"


class ReviewCreateView(CreateView):
    model = Review
    template_name = "review_form.html"
    form_class = ReviewForm
    success_url = 'Category_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["review_form"] = self.get_form()   # renamed form itself to differenciate it from the others
        return context

    def get_success_url(self):
        category_slug = self.kwargs['category_slug'] # get params
        product_slug = self.kwargs['product_slug'] # get params
        return reverse_lazy('Product_detail', kwargs={"category_slug": category_slug, "product_slug":product_slug})

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        category_slug = self.kwargs['category_slug'] # get params
        product_slug = self.kwargs['product_slug'] # get params
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        user =  self.request.user
        form.save(commit=False)
        form.instance.user = user
        form.instance.product = product
        form.save()
        return super(ReviewCreateView, self).form_valid(form)

class RatingCreateView(CreateView):
    model = Rating
    template_name = "rating_form.html"
    form_class = RatingForm
    success_url = 'Category_detail'

    def get(self, request, *args, **kwargs):
        category_slug = self.kwargs['category_slug'] # get params
        product_slug = self.kwargs['product_slug'] # get params
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        raters = [x.user for x in Rating.objects.filter(product=product)]
        user = request.user
        if user in raters:
            messages.info(request, 'you already rated this product')
            return redirect('Product_detail',category_slug=category_slug, product_slug=product_slug)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rating_form"] = self.get_form()   # renamed form itself to differenciate it from the others
        return context

    def get_success_url(self):
        category_slug = self.kwargs['category_slug'] # get params
        product_slug = self.kwargs['product_slug'] # get params
        return reverse_lazy('Product_detail', kwargs={"category_slug": category_slug, "product_slug":product_slug})

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        category_slug = self.kwargs['category_slug'] # get params
        product_slug = self.kwargs['product_slug'] # get params
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        user =  self.request.user
        form.save(commit=False)
        form.instance.user = user # assign values
        form.instance.product = product # assign values
        form.save()
        return super().form_valid(form)
        
         
    

    









# def update_review(request,category_slug, product_slug ,review_id):
#     product = Product.objects.get(category__slug=category_slug, slug=product_slug)
#     reviews = Review.objects.filter(product=product)
#     review = Review.objects.get(id=review_id,product=product)
#     print(reviews)
#     if request.method == 'POST':
#         form = ReviewForm(request.POST, instance=review)
#         if form.is_valid():
#             form.save()
#         return redirect('product_detail',category_slug=category_slug, product_slug=product_slug)    
#     else:
#         form = ReviewForm(instance=review)
#     return render(request, 'shop/product.html', {'form':form,'reviews':reviews, 'product':product})

# def remove_review(request,category_slug, product_slug, review_id):
#     product = Product.objects.get(category__slug=category_slug, slug=product_slug)
#     reviews = Review.objects.get(product=product,user=request.user,id=review_id)
    
#     reviews.delete()
#     return redirect('product_detail',category_slug=category_slug, product_slug=product_slug)