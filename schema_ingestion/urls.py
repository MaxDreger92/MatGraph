from django.urls import path
from . import views

app_name = 'schema_ingestion'

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
]