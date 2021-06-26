from django.db import models
from django.db.models import Avg
from django.db.models.fields import IntegerField
from django.urls.base import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200,db_index=True,unique=True, blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Category_detail", kwargs={"category_slug": self.slug})

    def save(self, *args, **kwargs):
        """override save methos for automatisition of repetitive stable data"""
        # create slugs automatically from product's name
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="products")
    slug = models.SlugField(max_length=50, db_index=True)
    stock = models.PositiveIntegerField(null=True, blank=True)
    available = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    discount = models.IntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-updated']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('Product_detail', kwargs={"category_slug": self.category.slug, "product_slug":self.slug})

    def save(self, *args, **kwargs):
        """override save methos for automatisition of repetitive stable data , and statuses"""
        # display avilability automatically from product's stock
        if self.stock > 0:
            self.available = True
        else:
            self.available = False
        # create slugs automatically from product's name
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def avg_ratings(self):
        """calculate average ratings as Intgers
        because aggregate returns a dict, ['rating__avg'] get the value"""
        return self.rating_products.aggregate(Avg('rating', output_field=IntegerField()))['rating__avg']
       
    def rate_list(self):
        """create a list from the average ratings to be able to display it as stars,
         the empty list is necessary to avoid NonType error"""
        
        try:
            return [x for x in range(self.avg_ratings())]
        except:
            return []



def upload_location(instance, filename):
    filebase ,extension = filename.split('.')
    # rename image by model's name, Django aitomatically add a random prefix to multiple images
    return 'products//%s.%s' % (instance.product.name, extension)

class Image(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to=upload_location, null=True, blank=True)

    class Meta:
        verbose_name = ("Image")
        verbose_name_plural = ("Images")
    def __str__(self):
        return self.product.name + str(self.id)

    def get_absolute_url(self):
        return reverse("Image_detail", kwargs={"category_slug":self.product.category.slug, "product_slug":self.product.slug, "image_id":self.id})

class Relation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, null=True,related_name='%(class)s_products')
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True,related_name='%(class)s_users')

    class Meta:
        abstract =True

class Review(Relation):
    comment = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = ("Review")
        verbose_name_plural = ("Reviews")

    def __str__(self):
        return  str(self.id)

    def get_absolute_url(self):
        return reverse("Review_detail", kwargs={"id": self.id})


class Rating(Relation):
    rating = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(10)],null=True, blank=True, default=None)

    class Meta:
        verbose_name = ("Rating")
        verbose_name_plural = ("Ratings")

    def __str__(self):
        return str(self.rating)






