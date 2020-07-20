from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from PIL import Image
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField






def user_img(instance, filename):
   name = instance.user.username
   slug = slugify(name)
   return 'user_img/%s/%s' %(slug, filename)

class Profile(models.Model):
   user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
   image = models.ImageField(upload_to=user_img, default="default.png", null=True, blank=True)
   phone = PhoneNumberField(blank=True, help_text='Phone Number')
   address = models.CharField(max_length=150)
   house_number = models.CharField(max_length=50, null=True, blank=True)
   zip_code = models.CharField(max_length=15, null=True, blank=True)
   city = models.CharField(max_length=50, null=True, blank=True)
   state = models.CharField(max_length=50, null=True, blank=True)
   created = models.DateTimeField(auto_now_add=True)
   updated = models.DateTimeField(auto_now_add=False, auto_now=True)
   
   def __str__(self):
      return f'{self.user.username} Profile'
   
   def save(self, *args, **kwargs):
      super(Profile, self).save(*args, **kwargs)


