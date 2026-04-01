from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from orders.models import Order
from .models import Payment
import requests
import json
from .tasks import send_payment_notification

MERCHANT_ID = "00000000-0000-0000-0000-000000000000" 
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json" 
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"   
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
CALLBACK_URL = "http://127.0.0.1:8000/api/payment/verify/" 

class PaymentStartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        
        total_price = 100000 
        amount_in_rial = total_price * 10 
        
        payment = Payment.objects.create(
            order=order,
            amount=total_price
        )
        
        req_data = {
            "merchant_id": MERCHANT_ID,
            "amount": amount_in_rial,
            "description": f"Payment for order number {order.id} at Sina Shop",
            "callback_url": CALLBACK_URL,
        }
        req_header = {"accept": "application/json", "content-type": "application/json"}
        
        try:
            res = requests.post(url=ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)
            res_data = res.json()
            
            if len(res_data['errors']) == 0 and res_data['data']['code'] == 100:
                authority = res_data['data']['authority']
                
                payment.ref_id = authority
                payment.save()
                
                payment_url = ZP_API_STARTPAY.format(authority=authority)
                return Response({"url": payment_url}, status=status.HTTP_200_OK)
                
            else:
                return Response({"error": res_data['errors']}, status=status.HTTP_400_BAD_REQUEST)
                
        except requests.exceptions.ConnectionError:
            return Response({"error": "Failed to connect to the bank server"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        
class PaymentVerifyView(APIView):
    
    def get(self, request):
        authority = request.GET.get('Authority')
        payment_status = request.GET.get('Status')

        payment = get_object_or_404(Payment, ref_id=authority)

        if payment_status != 'OK':
            payment.status = Payment.STATUS_FAILED
            payment.save()
            return Response({"message": "Payment failed or was canceled by the user."}, status=status.HTTP_400_BAD_REQUEST)

        if payment.status == Payment.STATUS_SUCCESS:
            return Response({"message": "This payment has already been verified."}, status=status.HTTP_200_OK)

        req_header = {"accept": "application/json", "content-type": "application/json"}
        req_data = {
            "merchant_id": MERCHANT_ID,
            "amount": int(payment.amount * 10),
            "authority": authority
        }

        try:
            res = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
            res_data = res.json()

            if len(res_data['errors']) == 0:
                code = res_data['data']['code']
                
                if code == 100 or code == 101:
                    payment.status = Payment.STATUS_SUCCESS
                    payment.save()

                    send_payment_notification.delay(payment.order.id, request.user.email)

                    ref_id = res_data['data']['ref_id']
                    
                    return Response({
                        "message": "Payment verified successfully.",
                        "tracking_code": ref_id
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Transaction failed.", "error_code": code}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": res_data['errors']}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.ConnectionError:
            return Response({"error": "Failed to connect to the bank server."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)