from django.shortcuts import render

from rest_framework.views import APIView

from .serializers import RegisterSerializer


class RegisterView(APIView):
    pass

# als ertes werden alle User geholt
# dann wird der Serializer geholt
# 
