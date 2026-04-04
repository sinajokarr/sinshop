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
from .tasks import send_payment_notification

class PaymentStartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        
        if Payment.objects.filter(order=order, status=Payment.STATUS_SUCCESS).exists():
            return Response({"error": "Order is already paid."}, status=status.HTTP_400_BAD_REQUEST)
            
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


class PaymentVerifyView(APIView):
    
    def get(self, request):
        authority = request.GET.get('Authority')
        payment_status = request.GET.get('Status')

        payment = get_object_or_404(Payment, ref_id=authority)

        if payment_status != 'OK':
            payment.status = Payment.STATUS_FAILED
            payment.save()
            return Response({"error": "Payment failed or canceled by user."}, status=status.HTTP_400_BAD_REQUEST)

        if payment.status == Payment.STATUS_SUCCESS:
            return Response({"message": "Payment already verified."}, status=status.HTTP_200_OK)

        req_header = {"accept": "application/json", "content-type": "application/json"}
        req_data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(payment.amount * 10),
            "authority": authority
        }

        try:
            res = requests.post(
                url=settings.ZARINPAL_VERIFY_URL, 
                data=json.dumps(req_data), 
                headers=req_header,
                timeout=10
            )
            res_data = res.json()

            if len(res_data['errors']) == 0:
                code = res_data['data']['code']
                
                if code == 100 or code == 101:
                    payment.status = Payment.STATUS_SUCCESS
                    payment.save()

                    send_payment_notification.delay(payment.order.id, payment.order.user.email)

                    return Response({
                        "message": "Payment verified successfully.",
                        "tracking_code": res_data['data']['ref_id']
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "error": "Transaction failed.", 
                        "code": code
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "error": "Bank verification failed.", 
                    "details": res_data['errors']
                }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException:
            return Response({
                "error": "Failed to connect to the bank server."
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)