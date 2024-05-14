from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class DataTestView(APIView):

    def get(self, request):
        return Response({"message": "API active"})
