from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.db.models import Q
from django.views.generic import ListView, DetailView, View
from .models import *
from .forms import *
from .forms import VariationInventoryFormSet
from django.utils import timezone
#from vanilla import DetailView

import random
import string
#Stripe API Key
import stripe
stripe.api_key = "sk_test_hHjrGycdvzUznbaj3gA24bwW00ZrjaRkFK"

# Create your views here.
def create_ref_code():
   return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


# Create your views here.
def home(request):
   products = Product.objects.all().order_by('?')
   category = Category.objects.all()
   new_products = Product.objects.filter(is_new=True)
   featured_products = Product.objects.filter(is_featured=True)
   
   context = {
      'products':products,
      'category':category,
      'new_products':new_products,
      'featured_products':featured_products
   }
   return render(request, "store/home_page.html", context)

def allProducts(request):
   products = Product.objects.all()
   category = Category.objects.all()
   
   context = {
      'products':products,
      'category':category
   }
   return render(request, "store/product_list.html", context)


def userProductOrdered(request):
   current_user = request.user
   category = Category.objects.all()
   #product = Product.objects.all()
   ordered_products = Order.objects.filter(user_id=current_user)
   
   context = {
      'category': category,
      'ordered_products':ordered_products
   }
   
   return render(request, "store/home_page.html", context)


def userProductOrdered(request, id):
   current_user = request.user
   category = Category.objects.all()
   order_product = OrderProduct.objects.filter(user_id=current_user)
   product = Product.objects.all()
   ordered_products = Order.objects.get(user_id=current_user, id=id)
   
   context = {
      'category': category,
      'product': product,
      'ordered_products':ordered_products
   }
   
   return render(request, "store/home_page.html", context)
   

''' class HomeView(ListView):
   model = Product
   queryset = Product.objects.all().order_by('?')
   paginate_by = 15
   template_name = "store/home.html"
   
   def get_context_data(self, *args, **kwargs):
      context = super(HomeView, self).get_context_data(**kwargs)
      context['new_products'] = Product.objects.all().is_new()#.order_by('?')
      return context  '''

   
class ProductDetailView(DetailView):
   model = Product
   """ paginate_by = 20"""
   #queryset = Product.objects.get(pk=pk)
   template_name = "store/detail_page.html"
   
   def get_context_data(self, *args, **kwargs):
      pk = self.kwargs.get('pk')
      instance = self.get_object()
      context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
      context['images'] = ProductImage.objects.filter(product_id=pk)
      context['category'] = Category.objects.all()
      context['related'] = Product.objects.get_related(instance).order_by('?')[:3]
      return context
 
   
   #Import random
   #context['related'] = sorted(Product.objects.get_related(instance)[:3], key=lambda x:random.ramdom()

   
class VariationView(ListView):
   model = Variation
   queryset = Variation.objects.all()
   
   def get_context_data(self, *args, **kwargs):
      context = super(VariationView, self).get_context_data(*args, **kwargs)
      context["formset"] = VariationInventoryFormSet(queryset=self.get_queryset)
      return context
   
   def get_queryset(self, *args, **kwargs):
      product_pk = self.kwargs.get('pk')
      if product_pk:
         product = get_object_or_404(Product, pk=product_pk)
         queryset  = Variation.objects.filter(product=product)
      return queryset
   
   def post(self, request, *args, **kwargs):
      print(request.POST)


def product_detail(request, pk, slug):
   #product = Product.objects.get(pk=pk)
   instance = request.get_object()
   product_list = Product.objects.get_related(instance)
   try:
      product = product_list.get(pk=pk)
   except Product.DoesNotExist:
      raise Http404
   images = ProductImage.objects.filter(product_id=pk)
   category = Category.objects.all()
   
   
   context = {
      'product': product,
      'images': images,
      'category':category,
   }
   return render(request, 'store/detail_page.html', context)



class SearchProduct(ListView):
   template_name = 'store/search_page.html'
   paginate_by = 10
   
   def get(self, *args, **kwargs):
      category = Category.objects.all()

      context = {
         'category':category
      }
      return render(self.request, 'store/search_page.html', context)
   
   def get_queryset(self, *args, **Kwargs): 
      request = self.request
      query = request.GET.get('q')
      if query is not None:
         lookups = Q(name__icontains=query)|Q(brand__icontains=query)|Q(description__icontains=query)|Q(price__icontains=query)
         return Product.objects.filter(lookups).distinct()
      return Product.objects.none()


@login_required(login_url='login-page')
def add_to_cart(request, pk, slug):
   product = get_object_or_404(Product, pk=pk, slug=slug)
   order_item, created = OrderProduct.objects.get_or_create(
      product=product,
      user= request.user,
      ordered = False
      )
   order_qs =  Order.objects.filter(user=request.user, ordered=False)
   if order_qs.exists():
      order = order_qs[0]
      # Checks if product is in order
      if  order.products.filter(product__slug=product.slug).exists():
         order_item.quantity += 1
         order_item.save()
         messages.success(request, "This product's quantity has been updated.")
         
      else:
         order.products.add(order_item)
         messages.success(request, "This product has been added to your cart.")
         
         
   else:
      ordered_date = timezone.now()
      order = Order.objects.create(user=request.user, ordered_date=ordered_date)
      order.products.add(order_item)
      
   return redirect('product-detail', pk=pk,  slug=slug)


@login_required(login_url='login-page')
def add_to_cart_home_page(request, slug):
   product = get_object_or_404(Product, slug=slug)
   order_item, created = OrderProduct.objects.get_or_create(
      product=product,
      user=request.user,
      ordered=False
   )
   order_qs = Order.objects.filter(user=request.user, ordered=False)
   if order_qs.exists():
      order = order_qs[0]
      # check if the order item is in the order
      if order.products.filter(product__slug=product.slug).exists():
         order_item.quantity += 1
         order_item.save()
         messages.info(request, "This item quantity was updated.")
         return redirect("/", slug=slug)
      else:
         order.products.add(order_item)
         messages.info(request, "This item was added to your cart.")
         return redirect("/", slug=slug)
   else:
      ordered_date = timezone.now()
      order = Order.objects.create(
         user=request.user, ordered_date=ordered_date)
      order.products.add(order_item)
      messages.info(request, "This item was added to your cart.")
      return redirect("/", slug=slug)
 

@login_required(login_url='login-page')
def remove_from_cart(request, pk, slug):
   product = get_object_or_404(Product, pk=pk, slug=slug)
   order_qs =  Order.objects.filter(
      user=request.user, 
      ordered=False
      )
   if order_qs.exists():
      order = order_qs[0]
      # Checks if product is in order
      if  order.products.filter(product__slug=product.slug).exists():
         order_item = OrderProduct.objects.filter(
            product=product,
            user = request.user,
            ordered=False
         )[0]
         order.products.remove(order_item)
         messages.warning(request, "This item has been removed from your cart.")
         return redirect("cart-summary")
         
      else:
         #message
         messages.info(request, "This item was not in your cart")
         return redirect('product-detail', pk=pk,  slug=slug)
      
   else:
      #message
      messages.info(request, "You do not have an active order")
      return redirect('product-detail', pk=pk,  slug=slug)
      
   return redirect('product-detail', pk=pk,  slug=slug)


@login_required(login_url='login-page')
def add_single_item_to_cart(request, pk, slug):
   product = get_object_or_404(Product, slug=slug)
   order_item, created = OrderProduct.objects.get_or_create(
      product=product,
      user=request.user,
      ordered=False
   )
   order_qs = Order.objects.filter(user=request.user, ordered=False)
   if order_qs.exists():
      order = order_qs[0]
      # check if the order item is in the order
      if order.products.filter(product__slug=product.slug).exists():
         order_item.quantity += 1
         order_item.save()
         messages.success(request, "This item quantity was updated.")
         return redirect("cart-summary")
      else:
         order.products.add(order_item)
         messages.success(request, "This item was added to your cart.")
         return redirect("cart-summary")
   else:
      ordered_date = timezone.now()
      order = Order.objects.create(
         user=request.user, ordered_date=ordered_date)
      order.product.add(order_item)
      messages.success(request, "This item was added to your cart.")
      return redirect("cart-summary")


@login_required(login_url='login-page')
def remove_single_item_from_cart(request, pk, slug):
   product = get_object_or_404(Product, pk=pk, slug=slug)
   order_qs = Order.objects.filter(
      user=request.user,
      ordered=False)
   if order_qs.exists():
      order = order_qs[0]
      # check if the order item is in the order
      if order.products.filter(product__slug=product.slug).exists():
         order_item = OrderProduct.objects.filter(
               product=product,
               user=request.user,
               ordered=False
         )[0]
         if order_item.quantity >1:
            order_item.quantity -= 1
            order_item.save()
         else:
            order.products.remove(order_item)
         order_item.save()
         messages.warning(request, "Product Quantity has been decreased.")
         return redirect("cart-summary")
      else:
         # add a message saying the user dosent have an order
         messages.info(request, "Product was not in your cart.")
         return redirect("cart-summary")
   else:
      # add a message saying the user dosent have an order
      messages.info(request, "You don't have an active order.")
      return redirect("cart-summary")


class CartSummaryView(LoginRequiredMixin, View):
   def get(self, *args, **kwargs):
      try:
         order = Order.objects.get(user=self.request.user, ordered=False)
         couponform = CouponForm()
         category = Category.objects.all()
         context = {
            'object':order,
            'couponform':couponform,
            'category': category
         }
         return render(self.request, 'store/cart.html', context)
      except ObjectDoesNotExist:
         messages.warning(self.request, "You don't have any active Orders")
         return redirect("/")
      return render(self.request, 'store/cart.html')
   

class CheckoutView(View):
   def get(self, *args, **kwargs):
      form = CheckoutForm()
      category = Category.objects.all()
      order = Order.objects.get(user=self.request.user, ordered=False)
      context = {
         'form':form,
         'category':category,
         'order':order
      }
      return render(self.request, 'store/checkout.html', context) 
   
   def post(self, *args, **kwargs):
      form = CheckoutForm(self.request.POST or None)
      try:
         order = Order.objects.get(user=self.request.user, ordered=False)
         if form.is_valid():
            street_address = form.cleaned_data.get('street_address')#['street_address']
            apartment_address = form.cleaned_data.get('apartment_address') #['apartment_address']
            address_2 = form.cleaned_data.get('address_2') #['address_2']
            phone_number = form.cleaned_data.get('phone_number')#['phone_number']
            city = form.cleaned_data.get('city') #['city']
            state = form.cleaned_data.get('state') #['state']
            zip_code = form.cleaned_data.get('zip_code')#['zip_code']
            #save_info = form.cleaned_data.get('save_info')
            payment_option = form.cleaned_data.get('payment_option') #['payment_option']
            
            shipping_address = Address (
               user = self.request.user,
               street_address = street_address,
               apartment_address = apartment_address,
               address_2 = address_2,
               phone_number = phone_number,
               city = city,
               state = state,
               zip_code = zip_code,
               #save_info = save_info,
               #payment_option = payment_option,
            )
            
            shipping_address.save()
            order.shipping_address = shipping_address
            order.save()
            #print(self.request.POST)
            ''' if payment_option == 'S':
               return redirect('payment', payment_option='stripe')
            elif payment_option == 'P':
               return redirect('payment',  payment_option='paypal')
            elif payment_option == 'COD':
               return redirect('success-page', payment_option='cash')
            else:
               messages.warning(self.request, 'Please select a Payment Option')
               return redirect('checkout-page') '''
            
            return redirect('payment')
         
         messages.warning(self.request, 'Failed Checkout, please try again')
         return redirect('checkout-page')
      
      except ObjectDoesNotExist:
         messages.warning(self.request, "You don't have any active Orders")
         return redirect("cart-summary")    
      

class PaymentView(View):
   def get(self, *args, **kwargs):
      category = Category.objects.all()
      order = Order.objects.get(user=self.request.user, ordered=False)
      if order.shipping_address:
         context = {
            'category':category,
            'order':order
         }
         return render(self.request, 'store/stripe_payment.html', context)
      else:
         messages.warning(self.request, 'You do not have a Shipping Address, Please add Shipping Address to Continue')
         return redirect('checkout-page')

   
   def post(self, *args, **kwargs):
      order = Order.objects.get(user=self.request.user, ordered=False)
      token = self.request.POST.get('stripeToken')
      amount = int(order.get_total() * 100) #paise = Rs 1 - for indian currency
      
      # Use Stripe's library to make requests...
      charge = stripe.Charge.create(
         amount=amount, 
         currency="inr",
         source=token
      )
      
      #Create Payment
      payment = Payment()
      payment.stripe_charge_id = charge['id']
      payment.user = self.request.user
      payment.amount = order.get_total()
      payment.save()
      
      #Assign Payment to order
      order_items = order.products.all()
      order_items.update(ordered=True)
      #Loop and save each other item
      for item in order_items:
         item.save()
      
      order.ordered = True
      order.payment = payment
      #Add reference code to oorder after payment
      order.ref_code = create_ref_code()
      order.save()
      
      #Successful Order
      messages.success(self.request, "Your Order payment was successful.")
      return redirect('success-page')
   

def successMsg(request):
   category = Category.objects.all()
   context = {'category':category}
   return render(request, 'store/success.html', context)   


def get_coupon(request, code):
   try:
      coupon = Coupon.objects.get(code=code)
      return coupon
   
   except ObjectDoesNotExist:
      messages.warning(request, 'Coupon code does not exist.')
      return redirect('cart-summary')
   
   
class AddCouponView(View):
   def post(self, *args, **kwargs):
      form = CouponForm(self.request.POST or None)
      if form.is_valid():
         try:
            code = form.cleaned_data['code']
            order = Order.objects.get(user=self.request.user, ordered=False)
            order.coupon = get_coupon(self.request, code)
            order.save()
            messages.success(self.request, "Discount Succesfully applied.")
            return redirect('cart-summary')
   
         except ObjectDoesNotExist:
            messages.warning(self.request, 'You do not have active order.')
            return redirect('cart-summary')
         
         #return None
     
   
class RequestRefundView(View):
   def get(self, *args, **kwargs):
      form = RefundForm(self.request.POST)
      category = Category.objects.all()

      context = {
         'form': form,
         'category':category
      }
      return render(self.request, 'store/refund.html', context)
   
   
   def post(self, *args, **kwargs):
      form = RefundForm(self.request.POST)
      if form.is_valid():
         ref_code = form.cleaned_data.get('ref_code')
         message = form.cleaned_data.get('message')
         email = form.cleaned_data.get('email')
         
         try:
            order = Order.objects.get(ref_code=ref_code)
            order.refund_requested = True
            order.save()
            
            refund = Refund()
            refund.order = order
            refund.reason = message
            refund.email = email
            refund.save()  
            
            #messages.info(self.request, "Your request was received and we'll get bact to you shortly.")
            return redirect('refund-success-msg')  
            
         except ObjectDoesNotExist:
               messages.info(self.request, 'This order does not exist.')
               return redirect('refund')  
            
def refundSuccessMsg(request):
   return render(request, 'store/refund_success.html')


class CommentView(View):
   def get(self, *args, **kwargs):
      form = ReviewForm()
      category = Category.objects.all()
      context = {
         'form':form,
         'category':category
      }
      return render(self.request, 'store/detail_page.html', context) 
   
   def post(self, *args, pk, slug, **kwargs):
      form = ReviewForm(self.request.POST or None)
      if form.is_valid():
         subject = form.cleaned_data['subject']
         rate = form.cleaned_data['rate']
         content = form.cleaned_data['content']
         
         review = ProductReview (
            user = self.request.user,
            product = get_object_or_404(Product, pk=pk, slug=slug),
            subject = subject,
            rate = rate,
            content = content,
         )
         
         review.save()
         
         messages.success(self.request, "Thanks for your Review")
         print(self.request.POST)
         #return HttpResponseRedirect('product-detail')
         
         return redirect('product-detail')

  

class ReviewView(View):
   form_class = ReviewForm
   template_name = 'detail_page.html'

   # Handle GET HTTP requests
   def get(self, request, *args, **kwargs):
      form = self.form_class(initial=self.initial)
      category = Category.objects.all()
      context = {
         'category':category,
         'form': form
         }
      return render(request, self.template_name, context)

   # Handle POST GTTP requests
   def post(self, request, *args, **kwargs):
      form = self.form_class(request.POST)
      if form.is_valid():
         subject = form.cleaned_data['subject']
         rate = form.cleaned_data['rate']
         content = form.cleaned_data['content']
         
         review = ProductReview (
            user = request.user,
            product = get_object_or_404(Product, kwargs=[self.pk, self.slug]),
            subject = subject,
            rate = rate,
            content = content,
         )
         # Save the review in the database (ProductReview Model)
         review.save()
         return HttpResponseRedirect('product-detail')

      return render(request, self.template_name, {'form': form})  
  
  
  

""" def review(request, pk, slug):
   url = request.META.get('HTTP_REFERRER') #this gets las url i.e  product detail page
   #return HttpResponse(url) #Just a test to display something on the page
   if request.method == 'POST':
      form = ReviewForm(request.POST)
      if form.is_valid():
         subject = form.cleaned_data['subject']
         rate = form.cleaned_data['rate']
         content = form.cleaned_data['content']
         
         review = ProductReview (
            user = request.user,
            product = get_object_or_404(Product, pk=pk, slug=slug),
            subject = subject,
            rate = rate,
            content = content,
         )
         # Save the review in the database (ProductReview Model)
         review.save()
         # Success Review Message
         messages.success(request, "Thanks for your Review")
         print(request.POST)
         #return HttpResponseRedirect(url)
         return HttpResponseRedirect('review', {'pk':pk, 'slug':slug})
      
         #return redirect('product-detail')
      
      return HttpResponseRedirect(url)
   
"""

def category(request, id, slug):
   category = Category.objects.all()
   category_products = Product.objects.filter(category_id=id)
   featured_products = Product.objects.filter(is_featured=True)
   
   context = {
      'category':category,
      'category_products': category_products,
      'featured_products':featured_products
   }
   #return HttpResponse(product)
   return render(request, 'store/category.html', context)

def category_list(request, id, slug):
   category = Category.objects.all()
   category_products = Product.objects.filter(category_id=id)
   context = {
      'category':category,
      'category_products': category_products
   }
   #return HttpResponse(product)
   return render(request, 'store/category_list.html', context)

