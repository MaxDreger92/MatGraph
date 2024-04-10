"""
The graphutils library contains classes that are needed to extend the django functionality on neo4j.

graphutils serializer classes:
 - GenericNeoViewSet
"""

from django.http import Http404
from rest_framework import viewsets


class GenericNeoViewSet(viewsets.GenericViewSet):

    def get_object(self):

        qs = self.get_queryset()

        try:
            return qs.get(uid=self.kwargs['pk'])
        except qs.source.DoesNotExist:
            raise Http404

    def get_queryset(self):
        ns = self.model.nodes
        if hasattr(self.model, 'label'):
            ns = ns.order_by('label')
        elif hasattr(self.model, 'uid'):
            ns = ns.order_by('uid')
        return ns
