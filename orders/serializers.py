from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart, CartItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return sum(item.quantity * item.unit_price for item in obj.items.all())

    class Meta:
        model = Order
        fields = ['id', 'user', 'placed_at', 'payment_status', 'total_price', 'items']
    
class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError("No cart with the given ID was found.")
        
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("The cart is empty.")
            
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user = self.context['user']
            
            cart = Cart.objects.select_for_update().get(id=cart_id)
            
            order = Order.objects.create(user=user)
            
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.final_price 
                ) for item in cart_items
            ]
            
            OrderItem.objects.bulk_create(order_items)                        
            cart.delete()
            
            return order