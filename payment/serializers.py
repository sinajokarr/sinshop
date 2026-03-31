from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'ref_id', 'status', 'created_at']
        read_only_fields = ['id', 'order', 'amount', 'ref_id', 'status', 'created_at']