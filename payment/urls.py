from django.urls import path
from . import views

urlpatterns = [
    
    path('pay/<int:pk>/', views.PaymentStartView.as_view(), name='payment-start'),  
    path('verify/', views.PaymentVerifyView.as_view(), name='payment-verify'),  
]
