from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from orders.models import Order
from .models import Payment
import requests


class PaymantStarView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post (self,request,pk):
        order = get_object_or_404(Order ,id= pk ,user= request.user )
        return Response({"message": "Ready to connect to bank..."})