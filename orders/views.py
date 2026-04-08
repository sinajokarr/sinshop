from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.response import Response
from .serializers import OrderSerializer, CreateOrderSerializer
from .models import Order

class OrderViewSet(mixins.CreateModelMixin, 
                   mixins.ListModelMixin, 
                   mixins.RetrieveModelMixin, 
                   GenericViewSet):
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')
        
    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        return OrderSerializer
    
    def get_serializer_context(self):
        return {'user': self.request.user}

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user': self.request.user}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        serializer_response = OrderSerializer(order)
        return Response(serializer_response.data)