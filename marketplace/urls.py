from django.urls import path
from . import views
app_name='marketplace'
urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('manage-orders/', views.marketplace_order_changelist, name='marketplace_order_changelist'),
    path('my-products/', views.my_products, name='my_products'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('process_checkout/', views.process_checkout, name='process_checkout'),
    path('gps/', views.gps, name='gps'),
    path('product/<int:product_id>/rate/', views.rate_product, name='rate_product'),
    path('top-selling/', views.top_selling_products, name='top_selling_products'),
    path('products/<int:product_id>/review/', views.submit_review, name='submit_review'),
    path('rate-product/', views.rate_product, name='rate_product'),
    path('send-verification/', views.send_verification, name='send_verification'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('check-otp/', views.check_otp, name='check_otp'),


]
