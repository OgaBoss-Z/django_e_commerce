from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from .views import (
   SearchProduct,
   ProductDetailView,
   CartSummaryView,
   CheckoutView,
   PaymentView,
   AddCouponView,
   RequestRefundView,
   RequestRefundView,
   #CommentView,
   ReviewView
   )
from . import views

urlpatterns = [
   path('', views.home, name='home-page'),
   path('products/', views.allProducts, name='products-page'),
   path('<pk>/<slug>/', ProductDetailView.as_view(), name='product-detail'),
   path('search', SearchProduct.as_view(), name='search-query'),
   path('add-to-cart/<pk>/<slug>/', views.add_to_cart, name='add-to-cart'),
   path("add-to-cart-home-page/", views.add_to_cart_home_page, name="add-to-cart-home-page"),   
   path('remove-from-cart/<pk>/<slug>/', views.remove_from_cart, name='remove-from-cart'),
   path('remove-item-from-cart/<pk>/<slug>/', views.remove_single_item_from_cart, name='remove-single-item-from-cart'),
   path("add-single-item-to-cart/<pk>/<slug>", views.add_single_item_to_cart, name="add-single-item-to-cart"),
   path("cart-summary/", CartSummaryView.as_view(), name="cart-summary"),
   path('checkout/', CheckoutView.as_view(), name='checkout-page'),
   path('payment/', PaymentView.as_view(), name='payment'),
   path('success/', views.successMsg, name='success-page'),
   path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
   path('refund/', RequestRefundView.as_view(), name='refund-page'),
   path('refund-successful/', views.refundSuccessMsg, name='refund-success-msg'),
   path('<pk>/<slug>/', ReviewView.as_view(), name='review'),
   path('category/<id>/<slug>/', views.category, name='category-page'),
]
