from django.urls import path
from .views import WorkflowMatcher

urlpatterns = [
    path('api/match/fabrication-workflow', WorkflowMatcher.as_view(), name='fabrication_workflow'),
]