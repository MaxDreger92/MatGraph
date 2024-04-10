from django.urls import path, include
from django.urls import re_path as url

from matgraph.views.baseViews import analyze, download, home, select_data
from matgraph.views.continuousDeploymentViews import github_webhook
from matgraph.views.matterView import ElementAutocompleteView, MaterialInputAutocompleteView, MaterialChoiceField
from matgraph.views.retrieveDataViews import download_data, download_data_form, FileRetrieveView
from matgraph.views.uploadDataViews import FileUploadView, upload_success, TableView, NodeLabelView, \
    NodeAttributeView, NodeView, GraphView

urlpatterns = [
    url(
        r'^autocomplete/element/$',
        ElementAutocompleteView.as_view(),
        name='element-autocomplete',
    ),
    url(
        r'^autocomplete/manufacturing/$',
        MaterialInputAutocompleteView.as_view(),
        name='material-input-autocomplete',
    ),
    url(
        r'^autocomplete/ontology/$',
        MaterialChoiceField,
        name='emmomatter-autocomplete'
    ),
    path('PIDA_ddl/<str:PID>/', download_data, name='download_data'),
    path('PIDA/<str:PID>/', download_data_form, name='download_data_form'),
    path('file_upload/', FileUploadView.as_view(), name='file_upload'),
    path('fileretrieval/<str:uid>/', FileRetrieveView.as_view(), name='file_retrieve'),
    path('upload_success/', upload_success, name='upload_success'),
    path('', home, name='home'),
    path('upload/', FileUploadView.as_view(), name='upload_csv'),
    path('download/', download, name='download'),
    path('analyze/', analyze, name='analyze'),
    path('select-data', select_data, name='select_data'),
    path('deploy/', github_webhook, name='github_webhook'),
    path('data/view/<str:identifier>/', TableView.as_view(), name='view_data'),
    path('data/label-extraction/<str:identifier>/', NodeLabelView.as_view(), name='label-extraction'),
    path('data/attribute-extraction/<str:identifier>/', NodeAttributeView.as_view(), name='attribute-extraction'),
    path('data/node-aggregation/<str:identifier>/', NodeView.as_view(), name='node-aggregation'),
    path('data/graph-construction/<str:identifier>/', GraphView.as_view(), name='graph-construction'),





]



