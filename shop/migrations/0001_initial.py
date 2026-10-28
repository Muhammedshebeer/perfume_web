# Generated for Classio initial schema — Django 5.2
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
import shop.models
import shop.validators

class Migration(migrations.Migration):
    initial=True
    dependencies=[]
    operations=[
        migrations.CreateModel(name='Brand',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('name',models.CharField(max_length=120,unique=True)),('slug',models.SlugField(unique=True))],options={'ordering':['name']}),
        migrations.CreateModel(name='Category',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('name',models.CharField(max_length=120,unique=True)),('slug',models.SlugField(unique=True))],options={'ordering':['name'],'verbose_name_plural':'Categories'}),
        migrations.CreateModel(name='Product',fields=[
          ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
          ('name',models.CharField(max_length=180)),('slug',models.SlugField(max_length=220,unique=True)),('description',models.TextField()),
          ('price',models.DecimalField(decimal_places=2,max_digits=10,validators=[django.core.validators.MinValueValidator(0)])),
          ('compare_at_price',models.DecimalField(blank=True,decimal_places=2,max_digits=10,null=True,validators=[django.core.validators.MinValueValidator(0)])),
          ('size_ml',models.PositiveIntegerField(default=100)),('concentration',models.CharField(default='Eau de Parfum',max_length=80)),
          ('top_notes',models.CharField(blank=True,max_length=250)),('heart_notes',models.CharField(blank=True,max_length=250)),
          ('base_notes',models.CharField(blank=True,max_length=250)),('sku',models.CharField(max_length=60,unique=True)),
          ('stock',models.PositiveIntegerField(default=0)),('image',models.ImageField(blank=True,upload_to=shop.models.product_image_path,validators=[shop.validators.validate_product_image])),
          ('image_alt',models.CharField(blank=True,max_length=220)),('is_featured',models.BooleanField(default=False)),('is_active',models.BooleanField(default=True)),
          ('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
          ('brand',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='products',to='shop.brand')),
          ('category',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='products',to='shop.category'))],options={'ordering':['-created_at']}),
        migrations.CreateModel(name='ProductImage',fields=[
          ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
          ('image',models.ImageField(upload_to=shop.models.gallery_image_path,validators=[shop.validators.validate_product_image])),
          ('alt_text',models.CharField(blank=True,max_length=220)),('sort_order',models.PositiveIntegerField(default=0)),
          ('created_at',models.DateTimeField(auto_now_add=True)),
          ('product',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='gallery',to='shop.product'))],options={'ordering':['sort_order','id']}),
        migrations.CreateModel(name='Inquiry',fields=[
          ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
          ('name',models.CharField(max_length=120)),('email',models.EmailField(max_length=254)),('phone',models.CharField(blank=True,max_length=40)),
          ('message',models.TextField()),('created_at',models.DateTimeField(auto_now_add=True)),('is_resolved',models.BooleanField(default=False)),
          ('product',models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='inquiries',to='shop.product'))],options={'ordering':['-created_at']}),
        migrations.CreateModel(name='Order',fields=[
          ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
          ('name',models.CharField(max_length=140)),('email',models.EmailField(max_length=254)),('phone',models.CharField(max_length=40)),
          ('address',models.TextField()),('city',models.CharField(max_length=80)),('notes',models.TextField(blank=True)),
          ('total',models.DecimalField(decimal_places=2,max_digits=12)),('status',models.CharField(choices=[('new','New'),('confirmed','Confirmed'),('shipped','Shipped'),('completed','Completed'),('cancelled','Cancelled')],default='new',max_length=20)),
          ('created_at',models.DateTimeField(auto_now_add=True))],options={'ordering':['-created_at']}),
        migrations.CreateModel(name='OrderItem',fields=[
          ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
          ('product_name',models.CharField(max_length=180)),('sku',models.CharField(max_length=60)),('quantity',models.PositiveIntegerField()),
          ('unit_price',models.DecimalField(decimal_places=2,max_digits=10)),
          ('order',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='items',to='shop.order')),
          ('product',models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='order_items',to='shop.product'))]),
    ]
