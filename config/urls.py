from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('apps.accounts.urls')),
    path('', include('apps.sky.urls')),
    path('', include('apps.customers.urls')),
    path('', include('apps.automations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )