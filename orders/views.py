from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet ,mixins ,ViewSet
from rest_framework.mixins import CreateModelMixin ,RetrieveModelMixin , ListModelMixin
from .serializers import OrderSerializer ,CreateOrderSerializer
from .models import Order , OrderItem
from cart.models import Cart
from rest_framework.response import Response
from django.db import transaction


class OrderViewSet (mixins.CreateModelMixin,ListModelMixin,RetrieveModelMixin,GenericViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset (self ):
        return Order.objects.filter(user=self.request.user)
        
        
    def get_serializer_class (self):
        if self.request.method == "POST" :
            return CreateOrderSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_id = serializer.validated_data['cart_id']    
        
        with transaction.atomic():
            cart = Cart.objects.get(id=cart_id)
            
            order = Order.objects.create(user=self.request.user)
            
            order_items = []
            
            for item in cart.items.all():
                new_order_item = OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.unit_price 
                )
                order_items.append(new_order_item)
            
            OrderItem.objects.bulk_create(order_items)
            cart.delete()
            
        serializer = OrderSerializer(order)
        return Response(serializer.data)