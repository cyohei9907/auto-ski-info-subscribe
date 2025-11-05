"""
WSGI config for auto_ski_info project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')

application = get_wsgi_application()