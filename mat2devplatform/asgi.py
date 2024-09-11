"""
ASGI config for mat2devplatform project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
import ray

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mat2devplatform.settings')

# ray.init(ignore_reinit_error=True)

application = get_asgi_application()
