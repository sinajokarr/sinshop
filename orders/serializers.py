from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        total = 0
        for item in obj.items.all():
            total += (item.quantity * item.unit_price)
        return total

    class Meta:
        model = Order
        fields = ['id', 'user', 'placed_at', 'items', 'total_price']