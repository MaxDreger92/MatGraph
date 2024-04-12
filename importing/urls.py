from django.urls import path

from importing.views import LabelExtractView, AttributeExtractView, NodeExtractView, GraphExtractView, GraphImportView

urlpatterns = [
    path('api/data/file-retrieve', LabelExtractView.as_view(), name='file-retrieve'),
    path('api/data/label-retrieve', AttributeExtractView.as_view(), name='label-retrieve'),
    path('api/data/attribute-retrieve', NodeExtractView.as_view(), name='attribute-retrieve'),
    path('api/data/node-retrieve', GraphExtractView.as_view(), name='node-retrieve',),
    path('api/data/graph-retrieve', GraphImportView.as_view(), name='graph-retrieve',)
]