from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.validators import slug_re
from django.db.models.aggregates import Avg, Count
from django.http import request
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.views.generic.base import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib import messages

from .models import Category, Product, Image, Rating, Review
from .forms import ReviewForm, RatingForm


# """Function Based Views"""

# def product_list(request, category_slug=None):
#     """return the whole list of existing products, can be filtered by category,research option, and paginated"""

#     images = Image.objects.all()
#     category = None # initialize to avoid "local variable 'category' referenced before assignment" error
#     search = request.GET.get('search','') # get name from html input, '' to avoid empty error
#     products = Product.objects.filter(available=True, name__icontains=search) # get all available product, stock > 0
#     if category_slug:
#         # get page by category
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

#     context = {'category': category,'products': products,'images':images,'page_obj':products}

#     return render(request,'list.html',context)


# def product_detail(request,category_slug,product_slug):
#     """retireve product by slug, reviews and list_image anduser, DRY concept"""

#     product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
#     reviews = Review.objects.filter(product=product)
#     user = request.user
#     images = product.images.all()

#     values = (product,reviews,images,user) # return tuple of queries

#     return values

# def image_detail(request,category_slug,product_slug,image_id):
#     """"retrieve image as its reel size"""

#     image = get_object_or_404(Image,product__category__slug=category_slug, product__slug=product_slug,id=image_id)
#     context = {'image':image}

#     return render(request,'image.html',context)

# def get_valids(product,user,category_slug,product_slug,form):
#     """DRY, form validation"""

#     if form.is_valid():
#         form = form.save(commit=False)
#         form.product = product
#         form.user = user    
#         form.save()
#         return redirect('Product_detail',category_slug=category_slug, product_slug=product_slug)

# def create_review(request,category_slug, product_slug):
#     """create review and product detail page with rating"""

#     # call function and retrieve values
#     product,reviews, images,user = product_detail(request,category_slug, product_slug) 
#     # call rating function
#     forma = rating_form(request,category_slug, product_slug,product,user)
#     if request.method == 'POST':
#         form = ReviewForm(data=request.POST)
#         # call validation function
#         get_valids(product,user,category_slug,product_slug,form)
#         return redirect('Product_detail',category_slug=category_slug, product_slug=product_slug)    
#     else:
#         form = ReviewForm()

#     context = {'review_form':form, 'product':product,'reviews':reviews,'images':images,'rating_form':forma}

#     return render(request, 'detail.html', context)

# def update_review(request,category_slug, product_slug ,review_id):
#     """update review and product detail page with rating"""
    
#     product,reviews, images,user = product_detail(request,category_slug, product_slug) 
#     review = Review.objects.get(id=review_id)
#     print(reviews)
#     if request.method == 'POST':
#         review_form = ReviewForm(request.POST, instance=review)
#         if review_form.is_valid():
#             review_form.save()
#         return redirect('Product_detail',category_slug=category_slug, product_slug=product_slug)    
#     else:
#         review_form = ReviewForm(instance=review)
#     return render(request, 'detail.html', {'review_form':review_form,'reviews':reviews, 'product':product,'review':review, 'images':images})

# def delete_review(request,category_slug, product_slug ,review_id):
#     """delete review"""

#     review = Review.objects.get(id=review_id)
#     review.delete()

#     return redirect('Product_detail',category_slug=category_slug, product_slug=product_slug)    

# def rating_form(request,category_slug, product_slug,product,user):
#     """allow users to rate product on time"""

#     # verify if the user already voted 
#     raters = [x.user for x in Rating.objects.filter(product=product)]
#     if user in raters:
#         return redirect('Product_detail',category_slug=category_slug, product_slug=product_slug)
#     else:
#         if request.method == 'POST':
#             form = RatingForm(data=request.POST)
#             # call validation function
#             get_valids(product,user,category_slug,product_slug,form)
#         else:
#             form = RatingForm()
#     return form



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

def get_context(self,context):       
        context["images"] = self.object.images.all() # display images with reverse raltion
        context["reviews"] = self.object.review_products.all().order_by('-created') # display images with reverse raltion
        context["review_form"] = ReviewForm() # display form for GET and POST requests
        context["rating_form"] = RatingForm() # display form for GET and POST requests

class ProductDetailView(DetailView):
    """get product detail, and ratings """
    model = Product
    template_name = "detail.html"
    slug_url_kwarg = 'product_slug' # to allow looking by slug instead of default pk, id
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_context(self,context)
        return context
       
class ImageDetailView(DetailView):
    """"show evry image as it reel size"""
    model = Image
    template_name = "image.html"
    context_object_name = "image"
    pk_url_kwarg = "image_id"

def get_kwargs(self):
    category_slug = self.kwargs['category_slug'] # get params
    product_slug = self.kwargs['product_slug'] # get params
    return category_slug, product_slug

def get_success_url(self):
        category_slug, product_slug = get_kwargs(self)
        return reverse_lazy('Product_detail', kwargs={"category_slug": category_slug, "product_slug":product_slug})

def get_form_valid(self, form):
        """If the form is valid, save the associated model."""
        category_slug, product_slug = get_kwargs(self)
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        user =  self.request.user
        form.save(commit=False)
        form.instance.user = user # assign values
        form.instance.product = product # assign values
        form.save()

class ReviewCreateView(CreateView):
    model = Review
    template_name = "detail.html"
    form_class = ReviewForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["review_form"] = self.get_form()   # renamed form itself to differenciate it from the others
        return context

    def get_success_url(self):
        return get_success_url(self)
  
    def form_valid(self, form):
        get_form_valid(self, form)
        return super().form_valid(form)  

class ReviewUpdateView(UpdateView):
    model = Review
    form_class = ReviewForm
    pk_url_kwarg = "review_id"
    template_name = "detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["review_form"] = self.get_form()   # renamed form itself to differenciate it from the others
        context["images"] = self.object.product.images.all()
        context["reviews"] = self.object.product.review_products.all().order_by('-created')
        context["product"] = self.object.product
        print('my context:',context)
        return context
    
    def get_success_url(self):
        return get_success_url(self)
        
class ReviewDeleteView(DeleteView):
    model = Review
    form_class = ReviewForm
    pk_url_kwarg = "review_id"

    def get_success_url(self):
        return get_success_url(self)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class RatingCreateView(CreateView):
    model = Rating
    template_name = "rating_form.html"
    form_class = RatingForm

    def get(self, request, *args, **kwargs):
        category_slug, product_slug = get_kwargs(self)
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        raters = [x.user for x in Rating.objects.filter(product=product)] # get list of raters
        user = request.user
        if user in raters:
            # prevent re-rate if already rated
            messages.info(request, 'you already rated this product')
            return redirect('Product_detail',category_slug=category_slug, product_slug=product_slug)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rating_form"] = self.get_form()   # renamed form itself to differenciate it from the others
        return context

    def get_success_url(self):
        return get_success_url(self)

    def form_valid(self, form):
        get_form_valid(self, form)
        return super().form_valid(form) 
    
class ProductPage(View):

    def get(self, request, *args, **kwargs):        
        return ProductDetailView.as_view()(self.request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        """call create review and update review classes"""
        if "comment" in request.POST:
            return ReviewCreateView.as_view()(self.request, *args, **kwargs)            
        elif "rating" in request.POST:          
            return RatingCreateView.as_view()(self.request,  *args, **kwargs)







