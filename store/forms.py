from django import forms
from django.forms.models import  modelformset_factory
from .models import Variation, ProductReview

#from django_countries.fields import CountryField
#from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.forms import UserCreationForm
from . import models

class VariationInventoryForm(forms.Form):
   class Meta:
      fields = ['price', 'sale_price']
      
VariationInventoryFormSet = modelformset_factory(Variation, form=VariationInventoryForm, extra=2)


PAYMENT_CHOICES = (
   ('COD', 'Cash'),
   ('S', 'Stripe'),
   ('P', 'PayPal'),
)

class CheckoutForm(forms.Form):
   #Shipping Address fields
   street_address = forms.CharField(widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Street address',
   }))
   apartment_address = forms.CharField(widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Apartment Address',
   }))
   address_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Optional Address',
   }))
   phone_number = forms.CharField(widget=forms.TextInput(attrs= {
      'placeholder': 'E.g, +123-987654321',
      'class': 'form-control'
   }))
   city = forms.CharField(widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter City',
   }))
   state = forms.CharField(widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Enter state',
   }))
   zip_code = forms.CharField(widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Zip/Postal Code',
   }))
   
   save_info = forms.BooleanField(required=False, widget=forms.TextInput(attrs={
      'class': 'form-control',
   }))
   
   payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
   code = forms.CharField(widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Coupon Code',
   }))


class RefundForm(forms.Form):
   ref_code = forms.CharField(widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Order Reference Code',
   }))
   message = forms.CharField(widget=forms.Textarea(attrs={
      'class': 'form-control',
      'placeholder': 'Reason for refund',
      'rows': 4
   }))
   email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Email Address'}))


class PaymentForm(forms.Form):
   stripeToken = forms.CharField(required=False)
   save = forms.BooleanField(required=False)
   use_default = forms.BooleanField(required=False)
   

class ReviewForm(forms.ModelForm):
   class Meta:
      model = ProductReview
      fields = ["subject", "rate", "content"]
   
          

