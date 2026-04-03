from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
import json

from orders.models import Order
from .models import Payment
from .serializers import PaymentSerializer

class PaymentStartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        
        total_price = order.get_total_price() 
        amount_in_rial = int(total_price * 10)
        
        payment = Payment.objects.create(
            order=order,
            amount=total_price
        )
        
        req_data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": amount_in_rial,
            "description": f"Payment for order number {order.id} at SINSHOP",
            "callback_url": settings.ZARINPAL_CALLBACK_URL,
        }
        req_header = {"accept": "application/json", "content-type": "application/json"}
        
        try:
            res = requests.post(
                url=settings.ZARINPAL_REQUEST_URL, 
                data=json.dumps(req_data), 
                headers=req_header,
                timeout=10 
            )
            res_data = res.json()
            
            if len(res_data['errors']) == 0 and res_data['data']['code'] == 100:
                authority = res_data['data']['authority']
                
                payment.ref_id = authority
                payment.save()
                
                serializer = PaymentSerializer(payment)
                payment_url = settings.ZARINPAL_STARTPAY_URL.format(authority=authority)
                
                return Response({
                    "payment_details": serializer.data,
                    "bank_url": payment_url
                }, status=status.HTTP_200_OK)
                
            else:
                return Response({
                    "error": "The bank rejected the request", 
                    "details": res_data['errors']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except requests.exceptions.RequestException:
            return Response({
                "error": "Failed to connect to the bank server"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)