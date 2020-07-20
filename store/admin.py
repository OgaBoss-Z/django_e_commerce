from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import *

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
   list_display = ['name', 'created']
   prepopulated_fields = {'slug': ('name',)}
   
   
class CategoryAdmin2(DraggableMPTTAdmin):
   mptt_indent_field = "name"
   list_display = ('tree_actions', 'indented_title',
                  'related_products_count', 'related_products_cumulative_count')
   list_display_links = ('indented_title',)
   prepopulated_fields = {'slug': ('name',)}

   def get_queryset(self, request):
      qs = super().get_queryset(request)

      # Add cumulative product count
      qs = Category.objects.add_related_count(
               qs,
               Product,
               'category',
               'products_cumulative_count',
               cumulative=True)

      # Add non cumulative product count
      qs = Category.objects.add_related_count(qs,
               Product,
               'category',
               'products_count',
               cumulative=False)
      return qs

   def related_products_count(self, instance):
      return instance.products_count
   related_products_count.short_description = 'Related products (for this specific category)'

   def related_products_cumulative_count(self, instance):
      return instance.products_cumulative_count
   related_products_cumulative_count.short_description = 'Related products (in tree)'

admin.site.register(Category, CategoryAdmin2)

# Define inline image fields for the admin  
class ImageInline(admin.TabularInline):
   model = ProductImage
   extra = 3
   
class VariationInline(admin.TabularInline):
   model = Variation
   extra = 0



# Register Product and ProductAdmin
class ProductAdmin(admin.ModelAdmin):
   list_display = ['name', 'price', 'discount_price', 'is_new', 'is_featured', 'created']
   list_filter = ['name', 'created']
   list_editable = ['discount_price', 'is_featured', 'is_new']
   prepopulated_fields = {'slug': ('name',)}
   inlines = [ImageInline, VariationInline]
admin.site.register(Product, ProductAdmin)

class ProductImageAdmin(admin.ModelAdmin):
   list_display = ['product', 'image']
admin.site.register(ProductImage, ProductImageAdmin)

class OrderAdmin(admin.ModelAdmin):
   list_display = ['user', 'ordered', 'received', 'shipping_address', 'being_delivered', 'refund_requested', 'refund_granted', 'ordered_date']
   list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted', 'ordered_date']
   search_fields = ['user__username', 'ref_code']
   #actions = [make_refund_accepted]
admin.site.register(Order, OrderAdmin)

class PaymentAdmin(admin.ModelAdmin):
   list_display = ['user', 'amount', 'timestamp', 'stripe_charge_id']
admin.site.register(Payment, PaymentAdmin)


admin.site.register(OrderProduct)
admin.site.register(ProductReview)
admin.site.register(Address)
admin.site.register(Coupon)
admin.site.register(Refund)

