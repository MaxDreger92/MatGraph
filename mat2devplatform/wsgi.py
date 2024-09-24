"""
WSGI config for mat2devplatform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import ray

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mat2devplatform.settings')

ray.init(ignore_reinit_error=True)

application = get_wsgi_application()
