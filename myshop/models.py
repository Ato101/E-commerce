from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser

class Category(models.Model):
    category_name = models.CharField(max_length=190,unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    description = models.TextField(max_length=225)
    cart_image = models.ImageField(upload_to='photos/category',blank=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def get_absolute_url(self):
        return reverse('myshop:products_by_category',args=[self.slug])


    def __str__(self):
        return self.category_name


class Product(models.Model):
    name = models.CharField(max_length=200,unique=True)
    description = models.TextField(max_length=500,blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products',blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200, unique=True)


    def get_absolute_url(self):
        return reverse('myshop:product_details',args=[self.category.slug,self.slug])

    def __str__(self):
        return self.name

class Cart(models.Model):
    cart_id = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.cart_id




variation_category_choice =(
    ('color','color'),
    ('size','size')
)
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)

    def sizes(self):
        return super(VariationManager,self).filter(variation_category ='size',is_active=True)

class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(choices=variation_category_choice,max_length=100)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value



class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation,blank=True)
    quantity = models.IntegerField()
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return self.product



