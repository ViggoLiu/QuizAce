from django.shortcuts import render

# Create your views here.
# user/views.py
from rest_framework.views import APIView
from rest_framework.response import Response

class TestView(APIView):
    def get(self, request):
        return Response({"message": "后端接口正常"})