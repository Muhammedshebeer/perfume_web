from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, Category, Product, ProductImage, Inquiry, Order, OrderItem

@admin.register(Brand,Category)
class TaxonomyAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('name',)}
    search_fields=['name']

class GalleryInline(admin.TabularInline):
    model=ProductImage
    extra=0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=['name','sku','brand','price','stock','is_active','preview']
    list_filter=['is_active','is_featured','brand','category']
    search_fields=['name','sku']
    prepopulated_fields={'slug':('name',)}
    inlines=[GalleryInline]
    def preview(self,obj):
        return format_html('<img src="{}" style="height:40px;width:40px;object-fit:cover">',obj.image.url) if obj.image else '—'
    # Main image required on create is enforced by ProductForm in the custom dashboard.

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display=['name','email','product','created_at','is_resolved']
    list_filter=['is_resolved']

class ItemInline(admin.TabularInline):
    model=OrderItem
    extra=0
    readonly_fields=['product','product_name','sku','quantity','unit_price']
    can_delete=False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=['id','name','email','total','status','created_at']
    list_filter=['status']
    readonly_fields=['name','email','phone','address','city','notes','total','created_at']
    inlines=[ItemInline]
