from django.urls import path
from .views import workflow_matcher_view, workflow_matcher

urlpatterns = [
    path('search/', workflow_matcher_view, name='matcher'),
    path('api/data/fabrication-workflow/', workflow_matcher, name='fabrication_workflow'),
]