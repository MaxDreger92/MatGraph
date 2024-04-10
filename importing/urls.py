from django.urls import path

from importing.views import LabelExtractView, AttributeExtractView, NodeExtractView, GraphExtractView, GraphImportView

urlpatterns = [
    path('api/file-retrieve', LabelExtractView.as_view(), name='file-retrieve'),
    path('api/label-retrieve', AttributeExtractView.as_view(), name='label-retrieve'),
    path('api/attribute-retrieve', NodeExtractView.as_view(), name='attribute-retrieve'),
    path('api/node-retrieve', GraphExtractView.as_view(), name='node-retrieve',),
    path('api/graph-retrieve', GraphImportView.as_view(), name='graph-retrieve',)
]