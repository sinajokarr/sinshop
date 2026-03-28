from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet ,mixins ,ViewSet
from rest_framework.mixins import CreateModelMixin ,RetrieveModelMixin , ListModelMixin
from serializers import OrderSerializer ,CreateOrderSerializer
from .models import Order , OrderItem


class OrderViewSet (mixins.CreateModelMixin,ListModelMixin,RetrieveModelMixin,GenericViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    def get_serializer_class (self):
        if self.request.method == "POST" :
            return CreateOrderSerializer
        return OrderSerializer
    