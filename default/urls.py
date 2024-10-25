from django.urls import path
from .views import DataTestView

urlpatterns = [
    path('api/test', DataTestView.as_view(), name='test'),
]