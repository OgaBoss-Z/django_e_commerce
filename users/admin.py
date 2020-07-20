from django.contrib import admin
from .models import Profile


# Define inline image fields for the admin  

class ProfileAdmin(admin.ModelAdmin):
   list_display = ['user', 'phone', 'created']
admin.site.register(Profile, ProfileAdmin)
