from django.urls import path
from .views import workflow_matcher_view, workflow_matcher

urlpatterns = [
    path('workflow/', workflow_matcher_view, name='matcher'),
    path('fabrication-workflow/', workflow_matcher, name='fabrication_workflow'),
    # Other url patterns...
]