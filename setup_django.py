import os
from dotenv import load_dotenv
import django

# Load environment variables from .env file (if you have one)
load_dotenv()  # This should load variables into os.environ

# Set up the Django environment for external scripts
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mat2devplatform.settings")
django.setup()