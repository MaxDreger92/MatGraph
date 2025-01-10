from django.urls import path
from . import views
from .views import TabbedFormsView, CreateSynthesisStepView

app_name = 'schema_ingestion'

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('lab_book/', CreateSynthesisStepView.as_view(), name='tabbed_forms'),
]


