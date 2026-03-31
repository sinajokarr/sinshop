from django.db import models
from orders.models import Order 

class Payment(models.Model):
    STATUS_PENDING = 'P'
    STATUS_SUCCESS = 'S'
    STATUS_FAILED = 'F'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed')
    ]

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='payments')    
    amount = models.DecimalField(max_digits=10, decimal_places=2)    
    ref_id = models.CharField(max_length=100, null=True, blank=True)    
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} | Order: {self.order.id} | Status: {self.status}"