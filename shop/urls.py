from django.urls import path
from . import views
urlpatterns=[
 path('',views.home,name='home'),
 path('shop/',views.catalog,name='catalog'),
 path('shop/<slug:slug>/',views.product_detail,name='product_detail'),
 path('about/',views.about,name='about'),
 path('contact/',views.contact,name='contact'),
 path('cart/',views.cart,name='cart'),
 path('cart/add/<int:pk>/',views.cart_add,name='cart_add'),
 path('cart/update/<int:pk>/',views.cart_update,name='cart_update'),
 path('checkout/',views.checkout,name='checkout'),
 path('order/success/<int:pk>/',views.order_success,name='order_success'),
 path('dashboard/',views.dashboard,name='dashboard'),
 path('dashboard/products/',views.manage_products,name='manage_products'),
 path('dashboard/products/add/',views.product_add,name='product_add'),
 path('dashboard/products/<int:pk>/edit/',views.product_edit,name='product_edit'),
 path('dashboard/products/<int:pk>/delete/',views.product_delete,name='product_delete'),
 path('dashboard/orders/',views.manage_orders,name='manage_orders'),
 path('dashboard/orders/<int:pk>/',views.manage_order_detail,name='manage_order_detail'),
 path('dashboard/inquiries/',views.manage_inquiries,name='manage_inquiries'),
]
