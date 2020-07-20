from django.contrib import admin
from django.urls import path, include
#from django.contrib.auth import views as auth_views
from users import views
#from .views import UserOrderView


urlpatterns = [
   path("login/", views.loginPage, name="login-page"),
   path("logout/", views.logoutUser, name="logout-page"),
   path("register/", views.registerPage, name="register-page"),
   path("dashboard/", views.dashboard, name="dashboard"),
   path("dashboard-update/", views.dashboard_update, name="dashboard-update"),
   path("orders/", views.user_orders, name="user-orders"),
   #path("order/<id>/", views.user_order_detail, name="user-order-detail"),
   #path('order/<int:id>/', UserOrderView.as_view(), name="order-detail"),
   
   
]