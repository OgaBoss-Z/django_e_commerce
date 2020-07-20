from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
   path('admin/', admin.site.urls),
   path('', include('store.urls')),
   path('', include('users.urls')),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    
# For Admin Page Personalisation
admin.site.site_header = "OgaBoss Admin"
admin.site.site_title = "OgaBoss Admin Portal"
admin.site.index_title = "Welcome To OgaBoss"