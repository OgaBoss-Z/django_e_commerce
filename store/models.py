from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.db.models.signals import post_save
from django.shortcuts import reverse
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor.fields import RichTextField
from PIL import Image
from mptt.models import MPTTModel, TreeForeignKey



# Create your models here.   
class ProductQuerySet(models.query.QuerySet):
   def available(self):
      return self.filter(available=True)
   

class ProductManager(models.Manager):
   def get_queryset(self):
      return ProductQuerySet(self.model,  using=self.db)
   
   def all(self, *args, **kwargs):
      return self.get_queryset().available()

   def get_related(self, instance):
      categories = self.get_queryset().filter(related_categories__in=instance.related_categories.all())
      default_cat = self.get_queryset().filter(default_category=instance.default_category)
      qs = (categories | default_cat).exclude(id=instance.id).distinct()
      return qs
   
class Category(MPTTModel):
   name = models.CharField(max_length=25, unique=True)
   parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
   slug = models.SlugField(max_length=25,)
   created = models.DateTimeField(auto_now_add=True)
   updated = models.DateTimeField(auto_now=True)

   class MPTTMeta:
      order_insertion_by = ['name']

   class Meta:
      unique_together = (('parent', 'slug',))
      verbose_name_plural = 'categories'
      
   def __str__(self):
      return self.name
   ''' def __str__(self):
      full_path = [self.name]
      p = self.parent
      while p is not None:
         full_path.append(p.name)
         p = p.parent
      return '/'.join(full_path[::-1])  '''

class Product(models.Model):
   name = models.CharField(max_length=100)
   slug = models.SlugField(max_length=110)
   display_img = models.ImageField(upload_to='pro_img')
   brand = models.CharField(max_length=50)
   category = TreeForeignKey('Category', null=True, blank=True, on_delete=models.CASCADE)
   key_features = RichTextField(null=True, blank=True,)
   description = RichTextField(null=True, blank=True,)
   specification = RichTextField()
   price = models.DecimalField(max_digits=10, decimal_places=2)
   discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
   available = models.BooleanField(default=True)
   is_featured = models.BooleanField(default=False)
   is_new = models.BooleanField(default=False)
   related_categories = models.ManyToManyField('Category', related_name='related_categories', blank=True)
   default_category = models.ForeignKey('Category', related_name='default_categories', on_delete=models.CASCADE, blank=True, null=True)
   created = models.DateTimeField(auto_now_add=True)
   updated = models.DateTimeField(auto_now=True)
   
   objects =  ProductManager()

   class Meta:
      ordering = ('name',)
      verbose_name = 'product'
      verbose_name_plural = 'products'
      
   def __str__(self):
      return '{}'.format(self.name)

   def get_absolute_url(self):
      return reverse("product-detail", kwargs={
         'pk': self.pk,
         'slug': self.slug,
      })
      

   def get_add_to_cart_url(self):
      return reverse("add-to-cart", kwargs={
         'pk':self.pk,
         'slug': self.slug
      })

   def get_add_to_cart_home_page_url(self):
      return reverse("add-to-cart-home-page")# kwargs={"slug": self.slug})

   def get_remove_from_cart_url(self):
      return reverse("remove-from-cart", kwargs={
         'pk':self.pk,
         'slug': self.slug
      })      
     
def image_upload_to(instance, filename):
   name = instance.product.name
   slug = slugify(name)
   return 'product_img/%s/%s' %(slug, filename)

class ProductImage(models.Model):
   product = models.ForeignKey(Product, on_delete=models.CASCADE)
   image = models.ImageField(upload_to=image_upload_to)
   created = models.DateTimeField(auto_now_add=True)
   updated = models.DateTimeField(auto_now=True)

      
class Variation(models.Model):
   product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
   name = models.CharField(max_length=50)
   price = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
   discount_price = models.FloatField(blank=True, null=True)
   active = models.BooleanField(default=True)
   inventory = models.PositiveIntegerField(null=True, blank=True)
   
   def __str__(self):
      return '{}'.format(self.name)
   
   def get_price(self):
      if self.discount_price != None:
         return self.discount_price
      else:
         return self.price
   
   def get_absolute_url(self):
       return self.product.get_absolute_url()
      
def product_post_saved_receiver(sender, instance, created, *args, **kwargs):
   product = instance
   varitions = product.variation_set.all()  
   if varitions.count() == 0:
      new_var = Variation()
      new_var.product = product
      new_var.name = 'Default variation'
      new_var.price = product.price
      new_var.discount_price = product.discount_price
      new_var.save()
      
post_save.connect(product_post_saved_receiver, sender=Product)


class OrderProduct(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   product = models.ForeignKey(Product, on_delete=models.CASCADE)
   quantity = models.IntegerField(default=1)
   ordered = models.BooleanField(default=False)   
   
   def __str__(self):
      return f'{self.quantity} of {self.product.name}'
   
   def get_total_item_price(self):
      return self.quantity * self.product.price

   def get_total_discount_item_price(self):
      return self.quantity * self.product.discount_price
   
   def get_amount_saved(self):
      return self.get_total_item_price() - self.get_total_discount_item_price()

   def get_final_price(self):
      if self.product.discount_price:
         return self.get_total_discount_item_price()
      return self.get_total_item_price()
   
   
DELIVERY_STATUS = (
   ('PD', 'Pending'),
   ('DD', 'Delivered'),
   ('RD', 'Refund Granted'),
)

class Order(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   ref_code = models.CharField(max_length=50, blank=True, null=True)
   products = models.ManyToManyField(OrderProduct)
   start_date = models.DateTimeField(auto_now_add=True)
   ordered_date = models.DateTimeField()
   ordered = models.BooleanField(default=False)
   shipping_address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True, null=True)
   payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
   coupon = models.ForeignKey( 'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
   being_delivered = models.BooleanField(default=False)
   received = models.BooleanField(default=False)
   refund_requested = models.BooleanField(default=False)
   refund_granted = models.BooleanField(default=False)

   def __str__(self):
      return '{}'.format(self.user.username)
   
   def sub_total(self):
      total = 0
      for order_item in self.products.all():
         total += order_item.get_final_price()
      return total
   
   def saved_total(self):
      total = 0
      for order_item in self.products.all():
         total += order_item.get_amount_saved()
      return total
   
   def get_total(self):
      total = 0
      discount = 0
      for order_item in self.products.all():
         total += order_item.get_final_price()
         if self.coupon:
            discount = total * self.coupon.amount
         total -= discount
      return total
   
   def discount_price(self):
      total = 0
      for order_item in self.products.all():
         total += order_item.get_final_price()
      if self.coupon:
         discount = total * self.coupon.amount
      return discount


class Address(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   street_address = models.CharField(max_length=100)
   apartment_address = models.CharField(max_length=50)
   address_2 =models.CharField(max_length=100)
   phone_number = PhoneNumberField(blank=True, help_text='Phone Number')
   city = models.CharField(max_length=50)
   state = models.CharField(max_length=50)
   zip_code = models.CharField(max_length=10)
   
   def __str__(self):
      return self.user.username


class Payment(models.Model):
   stripe_charge_id = models.CharField(max_length=50)
   user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
   amount = models.FloatField()
   timestamp = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return self.user.username
   
   def payment_option(self):
      return reverse("payment", kwargs={
         'payment_option':payment_option
      })
      
      
class Coupon(models.Model):
   code = models.CharField(max_length=15)
   amount = models.DecimalField(max_digits=2, decimal_places=1)

   def __str__(self):
      return self.code
   
   def get_discou(self):
      percentage = self.amount * 100
      return percentage
   
   
class Refund(models.Model):
   order = models.ForeignKey(Order, on_delete=models.CASCADE)
   reason = models.TextField()
   accepted = models.BooleanField(default=False)
   email = models.EmailField()

   def __str__(self):
      return f"{self.pk}"


class ProductReview(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
   product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
   subject = models.CharField(max_length=100)
   rate = models.PositiveIntegerField(default=1, blank=True, null=True)
   content = models.TextField()
   created = models.DateTimeField(auto_now_add=True)
   updated = models.DateTimeField(auto_now=True)
   
   def __str__(self):
      return self.user.username
   
   def get_review_url(self):
      return reverse("review", kwargs={
         'pk':self.pk,
         'slug': self.slug
      })
   