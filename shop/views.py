from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import F, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import ProductForm, InquiryForm, CheckoutForm
from .models import Brand, Category, Product, ProductImage, Inquiry, Order, OrderItem
from .validators import validate_product_image
from django.core.exceptions import ValidationError
from django.conf import settings

staff_only = user_passes_test(lambda u:u.is_active and u.is_staff, login_url='login')

def home(request):
    return render(request,'shop/home.html',{'featured':Product.objects.filter(is_active=True,is_featured=True).select_related('brand')[:8],
        'latest':Product.objects.filter(is_active=True).select_related('brand')[:4]})

def catalog(request):
    products=Product.objects.filter(is_active=True).select_related('brand','category')
    query=request.GET.get('q','').strip()[:100]
    brand=request.GET.get('brand','')
    category=request.GET.get('category','')
    sort=request.GET.get('sort','newest')
    if query: products=products.filter(Q(name__icontains=query)|Q(brand__name__icontains=query)|Q(description__icontains=query))
    if brand: products=products.filter(brand__slug=brand)
    if category: products=products.filter(category__slug=category)
    if sort=='price_asc': products=products.order_by('price')
    elif sort=='price_desc': products=products.order_by('-price')
    elif sort=='name': products=products.order_by('name')
    return render(request,'shop/catalog.html',{'products':products,'brands':Brand.objects.all(),
        'categories':Category.objects.all(),'query':query,'selected_brand':brand,'selected_category':category,'sort':sort})

def product_detail(request,slug):
    product=get_object_or_404(Product.objects.select_related('brand','category').prefetch_related('gallery'),slug=slug,is_active=True)
    related=Product.objects.filter(is_active=True,category=product.category).exclude(pk=product.pk).select_related('brand')[:4]
    form=InquiryForm(request.POST or None)
    if request.method=='POST':
        if form.is_valid():
            inquiry=form.save(commit=False)
            inquiry.product=product
            inquiry.save()
            messages.success(request,'Thank you. Your enquiry has been received.')
            return redirect(product.get_absolute_url())
    return render(request,'shop/detail.html',{'product':product,'related':related,'inquiry_form':form})

def about(request): return render(request,'shop/about.html')

def contact(request):
    form=InquiryForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,'Your message was sent successfully.')
        return redirect('contact')
    return render(request,'shop/contact.html',{'form':form})

def _cart_rows(request):
    cart=request.session.get('cart',{})
    ids=[int(k) for k in cart if str(k).isdigit()]
    products=Product.objects.filter(pk__in=ids,is_active=True).select_related('brand')
    rows=[]
    for p in products:
        quantity=max(0,min(99,int(cart.get(str(p.pk),0))))
        if quantity:
            rows.append({'product':p,'quantity':quantity,'subtotal':p.price*quantity})
    return rows, sum((r['subtotal'] for r in rows), Decimal('0.00'))

def cart(request):
    rows,total=_cart_rows(request)
    return render(request,'shop/cart.html',{'rows':rows,'total':total})

@require_POST
def cart_add(request,pk):
    product=get_object_or_404(Product,pk=pk,is_active=True)
    if product.stock < 1:
        messages.error(request,'This product is out of stock.')
        return redirect(product.get_absolute_url())
    try: qty=max(1,min(int(request.POST.get('quantity','1')),99))
    except ValueError: qty=1
    session_cart=request.session.get('cart',{})
    key=str(product.pk)
    session_cart[key]=min(99,product.stock,int(session_cart.get(key,0))+qty)
    request.session['cart']=session_cart
    messages.success(request,f'{product.name} added to your bag.')
    return redirect('cart')

@require_POST
def cart_update(request,pk):
    cart_data=request.session.get('cart',{})
    key=str(pk)
    try: qty=int(request.POST.get('quantity','0'))
    except ValueError: qty=0
    product=Product.objects.filter(pk=pk,is_active=True).first()
    if not product or qty<=0:
        cart_data.pop(key,None)
    else:
        cart_data[key]=min(99,product.stock,qty)
        if not cart_data[key]: cart_data.pop(key,None)
    request.session['cart']=cart_data
    return redirect('cart')

def checkout(request):
    rows,total=_cart_rows(request)
    if not rows:
        messages.info(request,'Add something to your bag before checkout.')
        return redirect('catalog')
    form=CheckoutForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            # Conditional DB update prevents overselling when multiple shoppers check out.
            for row in rows:
                updated=Product.objects.filter(pk=row['product'].pk,is_active=True,
                    stock__gte=row['quantity']).update(stock=F('stock')-row['quantity'])
                if not updated:
                    messages.error(request,f"Not enough stock for {row['product'].name}. Please update your bag.")
                    return redirect('cart')
            order=form.save(commit=False)
            order.total=total
            order.save()
            OrderItem.objects.bulk_create([OrderItem(order=order,product=r['product'],product_name=r['product'].name,
                sku=r['product'].sku,quantity=r['quantity'],unit_price=r['product'].price) for r in rows])
        request.session['cart']={}
        request.session['last_order_id']=order.pk
        return redirect('order_success',pk=order.pk)
    return render(request,'shop/checkout.html',{'form':form,'rows':rows,'total':total})

def order_success(request,pk):
    if request.session.get('last_order_id') != pk:
        raise Http404()
    order=get_object_or_404(Order,pk=pk)
    return render(request,'shop/success.html',{'order':order})

@staff_only
def dashboard(request):
    return render(request,'dashboard/home.html',{
        'product_count':Product.objects.count(),'order_count':Order.objects.count(),
        'inquiry_count':Inquiry.objects.filter(is_resolved=False).count(),
        'revenue':Order.objects.exclude(status='cancelled').aggregate(total=Sum('total'))['total'] or 0,
        'recent_orders':Order.objects.all()[:6],
        'low_stock':Product.objects.filter(stock__lte=5,is_active=True).order_by('stock')[:6],
    })

@staff_only
def manage_products(request):
    products=Product.objects.select_related('brand','category').all()
    q=request.GET.get('q','').strip()[:100]
    if q: products=products.filter(Q(name__icontains=q)|Q(sku__icontains=q))
    return render(request,'dashboard/products.html',{'products':products,'query':q})

def _product_editor(request, product=None):
    editing=product is not None
    form=ProductForm(request.POST or None,request.FILES or None,instance=product)
    errors=[]
    if request.method=='POST':
        uploads=request.FILES.getlist('gallery_images')
        if len(uploads)>12: errors.append('Upload no more than 12 gallery images at once.')
        existing_ids={im.pk for im in product.gallery.all()} if editing else set()
        remove_ids=set()
        for value in request.POST.getlist('remove_gallery'):
            try:
                id_num=int(value)
                if id_num in existing_ids: remove_ids.add(id_num)
            except ValueError: pass
        if len(existing_ids-remove_ids)+len(uploads)>12:
            errors.append('A product can have at most 12 gallery images.')
        for upload in uploads:
            try: validate_product_image(upload)
            except ValidationError as exc: errors.append(f'{upload.name}: {"; ".join(exc.messages)}')
        # Reject an attempted main-image removal unless a replacement is uploaded.
        if request.POST.get('remove_main') and not request.FILES.get('image'):
            errors.append('Upload a replacement main image before removing the current one.')
        if form.is_valid() and not errors:
            with transaction.atomic():
                old_image_name=product.image.name if editing and product.image else None
                old_storage=product.image.storage if editing and product.image else None
                saved=form.save()
                if old_image_name and request.FILES.get('image') and old_image_name!=saved.image.name:
                    transaction.on_commit(lambda st=old_storage,n=old_image_name: st.delete(n))
                if remove_ids:
                    ProductImage.objects.filter(product=saved,pk__in=remove_ids).delete()
                for i,upload in enumerate(uploads):
                    ProductImage.objects.create(product=saved,image=upload,
                        alt_text=f'{saved.name} gallery image {i+1}',sort_order=saved.gallery.count())
            messages.success(request,'Product updated successfully.' if editing else 'Product created successfully.')
            return redirect('manage_products')
    return render(request,'dashboard/product_form.html',{'form':form,'product':product,'editing':editing,
        'upload_errors':errors,'max_image_mb':settings.MAX_PRODUCT_IMAGE_MB})

@staff_only
def product_add(request): return _product_editor(request)

@staff_only
def product_edit(request,pk):
    return _product_editor(request,get_object_or_404(Product.objects.prefetch_related('gallery'),pk=pk))

@staff_only
@require_POST
def product_delete(request,pk):
    product=get_object_or_404(Product,pk=pk)
    product.delete()
    messages.success(request,'Product deleted.')
    return redirect('manage_products')

@staff_only
def manage_orders(request):
    return render(request,'dashboard/orders.html',{'orders':Order.objects.all()})

@staff_only
def manage_order_detail(request,pk):
    order=get_object_or_404(Order.objects.prefetch_related('items'),pk=pk)
    if request.method=='POST':
        value=request.POST.get('status')
        if value in dict(Order.STATUS_CHOICES):
            order.status=value;order.save(update_fields=['status'])
            messages.success(request,'Order status updated.')
            return redirect('manage_order_detail',pk=pk)
        messages.error(request,'Invalid order status.')
    return render(request,'dashboard/order_detail.html',{'order':order,'statuses':Order.STATUS_CHOICES})

@staff_only
def manage_inquiries(request):
    if request.method=='POST':
        inquiry=get_object_or_404(Inquiry,pk=request.POST.get('inquiry_id'))
        inquiry.is_resolved=request.POST.get('resolved')=='1'
        inquiry.save(update_fields=['is_resolved'])
        messages.success(request,'Enquiry status updated.')
        return redirect('manage_inquiries')
    return render(request,'dashboard/inquiries.html',{'inquiries':Inquiry.objects.select_related('product').all()})
