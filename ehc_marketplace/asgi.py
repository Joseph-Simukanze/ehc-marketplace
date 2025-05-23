# ehc_marketplace/asgi.py

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehc_marketplace.settings')

application = get_asgi_application()
