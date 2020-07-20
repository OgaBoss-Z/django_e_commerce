from django import forms
from django.contrib.auth.models import User
#from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.modelfields import PhoneNumberField
#from phonenumber_field.widgets import PhoneNumberPrefixWidget
#from phone_field import PhoneField
from .models import Profile


class SignUpForm(UserCreationForm):
   username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
   first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
   last_name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
   email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Email Address'}))
   password1=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
   password2=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

   class Meta(UserCreationForm.Meta):
      model = User
      # fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)
      fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)


class UserUpdateForm(forms.ModelForm):
   first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
   last_name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
   
   class Meta:
      model = User
      fields = ['first_name', 'last_name',]


class ProfileUpdateForm(forms.ModelForm):
   phone = PhoneNumberField()
   #phone = PhoneNumberField(widget=forms.TextInput(attrs={'class': 'form-control'}))
   #phone = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
   address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
   house_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
   zip_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
   city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',}))
   state = forms.CharField(widget=forms.TextInput(attrs={ 'class': 'form-control'}))
   
   class Meta:
      model = Profile
      fields = ['phone', 'address', 'house_number', 'zip_code', 'city', 'state', 'image']
      
   
   def __init__(self, *args, **kwargs):
      super(ProfileUpdateForm, self).__init__(*args, **kwargs)
      self.fields['phone'].widget.attrs={'class': 'form-control'}


