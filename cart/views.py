from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

class CartViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny] 


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])