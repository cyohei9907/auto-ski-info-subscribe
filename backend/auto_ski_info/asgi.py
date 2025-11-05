"""
ASGI config for auto_ski_info project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')

application = get_asgi_application()