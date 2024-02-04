from django.urls import path

from importing.views import LabelExtractView, AttributeExtractView, NodeExtractView, GraphExtractView

urlpatterns = [
    path('api/file-retrieve', LabelExtractView.as_view(), name='file-retrieve'),
    path('api/label-retrieve', AttributeExtractView.as_view(), name='file-retrieve'),
    path('api/attribute-retrieve', NodeExtractView.as_view(), name='file-retrieve'),
    path('api/node-retrieve', GraphExtractView.as_view(), name='file-retrieve',)


]