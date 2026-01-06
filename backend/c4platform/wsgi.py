"""
WSGI config for C4 Platform project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'c4platform.settings')
application = get_wsgi_application()
