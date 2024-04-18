from django.urls import path
from .views import DataTestView

urlpatterns = [
    path('api/data/api-active-status', DataTestView.as_view(), name='api-active-status'),
]