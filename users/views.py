from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import *
from .forms import *
from store.models import Category, Order, OrderProduct
from django.db.models import Q

# Create your views here.
def registerPage(request):
   if request.user.is_authenticated:
      return redirect('home-page')
   else:
      form = SignUpForm()
      if request.method == 'POST':
         form = SignUpForm(request.POST)
         if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Your Account has been successfully created, Please login to Your Account @'+ user)
            return redirect('login-page')
      category = Category.objects.all()
      context = {
         'form': form,
         'category': category
         }
      return render(request, 'users/register.html', context)


def loginPage(request):
   if request.user.is_authenticated:
      return redirect('home-page')
   else:
      if request.method == 'POST':
         username = request.POST.get('username')
         password = request.POST.get('password')
         
         user = authenticate(request, username=username, password=password)
         if user is not None:
            login(request, user)
            return redirect('home-page')
         else:
            messages.info(request, 'Username or Password is incorrect!')
      category = Category.objects.all()
      context = {'category':category}
      return render(request, 'users/login.html', context)
   

   #def clean(self):
    #    username = self.cleaned_data.get('username')
     #   password = self.cleaned_data.get('password')
      #  user = authenticate(username=username, password=password)
       # if not user or not user.is_active:
        #    raise forms.ValidationError("Sorry, Invalid Credentials. Please try again.")
        #return self.cleaned_data


def logoutUser(request):
   if request.user.is_authenticated:
      logout(request)
      messages.info(request, 'You have successfull logged Out')
      return redirect('home-page')
   else:
      return redirect('home-page')


@login_required(login_url='login-page')
def dashboard(request):
   category = Category.objects.all()
   current_user = request.user
   user_orders = Order.objects.filter(user_id=current_user.id)[::-2]
   context = {
      'category':category,
      'user_orders':user_orders
      }
   return render(request, 'users/dashboard.html', context)


@login_required(login_url='login-page')
def dashboard_update(request):
   if request.method == 'POST':
      u_form = UserUpdateForm(request.POST, instance=request.user)
      p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
      if u_form.is_valid() and p_form.is_valid():
         u_form.save()
         p_form.save()
         messages.success(request, f'Your Profile Was Updated Successfully')
         return redirect('dashboard')
   else:
      u_form = UserUpdateForm(instance=request.user)
      p_form = ProfileUpdateForm(instance=request.user.profile)
      
   category = Category.objects.all()
   context = {
      'u_form': u_form,
      'p_form': p_form,
      'category':category
   }
   return render(request, 'users/dashboard_update.html', context)


@login_required(login_url='login-page')
def user_orders(request):
   current_user = request.user
   category = Category.objects.all()
   user_orders = Order.objects.filter(user_id=current_user.id)
   context = {
      'category':category,
      'user_orders':user_orders
   }
   return render(request, 'users/user_orders.html', context)
   
   
@login_required(login_url='login-page')
def user_order_detail(request, id):
   current_user = request.user
   category = Category.objects.all()
   order = Order.objects.get(user_id=current_user.id, id=id)
   order_items = OrderProduct.objects.filter(order_id=id)
   context = {
      'category':category,
      'order':order,
      'order_items':order_items
   }
   return render(request, 'users/user_order_detail.html', context)





   
''' class UserOrderView(LoginRequiredMixin, View):
   def get(self, id, *args, **kwargs):
      try:
         order = Order.objects.get(user=self.request.user,)
         order_items = OrderProduct.objects.filter(order_id=id)
         category = Category.objects.all()
         context = {
            'object':order,
            'order_items':order_items,
            'category': category
         }
         return render(self.request, 'users/user_order_detail.html', context)
      except ObjectDoesNotExist:
         messages.warning(self.request, "You don't have any active Orders")
         return redirect("/")
      return render(self.request, 'users/dashboard.html')
 '''