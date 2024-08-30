from django.urls import path
from .views import workflow_matcher

urlpatterns = [
    path('api/match/fabrication-workflow', workflow_matcher, name='fabrication_workflow'),
]