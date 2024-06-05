from django.urls import path

from importing.views import LabelExtractView, AttributeExtractView, NodeExtractView, GraphExtractView, GraphImportView

urlpatterns = [
    path('api/import/label-extract', LabelExtractView.as_view(), name='label-extract'),
    path('api/import/attribute-extract', AttributeExtractView.as_view(), name='attribute-extract'),
    path('api/import/node-extract', NodeExtractView.as_view(), name='node-extract'),
    path('api/import/graph-extract', GraphExtractView.as_view(), name='graph-extract',),
    path('api/import/graph-import', GraphImportView.as_view(), name='graph-import',)
]