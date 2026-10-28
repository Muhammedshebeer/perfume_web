from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Brand, Category

class Command(BaseCommand):
    help='Create a few initial fragrance brands and categories (no stock or fake products).'
    def handle(self,*args,**options):
        for name in ['Classio Signature','Atelier Collection','Maison Reserve']:
            Brand.objects.get_or_create(slug=slugify(name),defaults={'name':name})
        for name in ['For Her','For Him','Unisex','Discovery Sets']:
            Category.objects.get_or_create(slug=slugify(name),defaults={'name':name})
        self.stdout.write(self.style.SUCCESS('Brands and categories created. Now add real products and images in the dashboard.'))
