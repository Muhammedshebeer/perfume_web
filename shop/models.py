import uuid
from pathlib import Path
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from .validators import validate_product_image

def product_image_path(instance, filename):
    return f'products/{uuid.uuid4().hex}{Path(filename).suffix.lower()}'

def gallery_image_path(instance, filename):
    return f'products/gallery/{uuid.uuid4().hex}{Path(filename).suffix.lower()}'

class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    def __str__(self): return self.name
    class Meta: ordering=['name']

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    def __str__(self): return self.name
    class Meta: verbose_name_plural='Categories'; ordering=['name']

class Product(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    compare_at_price = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True,validators=[MinValueValidator(0)])
    size_ml = models.PositiveIntegerField(default=100)
    concentration = models.CharField(max_length=80, default='Eau de Parfum')
    top_notes = models.CharField(max_length=250, blank=True)
    heart_notes = models.CharField(max_length=250, blank=True)
    base_notes = models.CharField(max_length=250, blank=True)
    sku = models.CharField(max_length=60, unique=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=product_image_path, validators=[validate_product_image], blank=True)
    image_alt = models.CharField(max_length=220,blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering=['-created_at']
    def __str__(self): return self.name
    def get_absolute_url(self): return reverse('product_detail', kwargs={'slug':self.slug})
    @property
    def main_alt(self): return self.image_alt or f'{self.name} by {self.brand.name} perfume bottle'

class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='gallery')
    image = models.ImageField(upload_to=gallery_image_path, validators=[validate_product_image])
    alt_text = models.CharField(max_length=220,blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['sort_order','id']
    def __str__(self): return f'{self.product.name} image {self.pk}'
    @property
    def display_alt(self): return self.alt_text or f'{self.product.name} additional product view'

class Inquiry(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, null=True, related_name='inquiries')
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40,blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    class Meta: ordering=['-created_at']
    def __str__(self): return f'Inquiry from {self.name}'

class Order(models.Model):
    STATUS_CHOICES=[('new','New'),('confirmed','Confirmed'),('shipped','Shipped'),('completed','Completed'),('cancelled','Cancelled')]
    name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    address = models.TextField()
    city = models.CharField(max_length=80)
    notes = models.TextField(blank=True)
    total = models.DecimalField(max_digits=12,decimal_places=2)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']
    def __str__(self): return f'Order #{self.pk}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,related_name='order_items',null=True)
    product_name = models.CharField(max_length=180)
    sku = models.CharField(max_length=60)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10,decimal_places=2)
    def __str__(self): return f'{self.product_name} x {self.quantity}'
    @property
    def subtotal(self): return self.unit_price * self.quantity
