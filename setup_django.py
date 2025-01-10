import os
import django

# Set up the Django environment for external scripts
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
django.setup()