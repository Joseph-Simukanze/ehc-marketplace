from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
 # Import views from the current package (ehc_marketplace)

urlpatterns = [
     # Root URL for home_view
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('marketplace.urls')),  # Prefixed marketplace URLs
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
    path('chatbot/', include('chatbot.urls', namespace='chatbot')),
# ehc_marketplace/urls.py
    path('mtn/', include('payments.mtn.urls')),
    path('chat/', include('chat.urls')),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)