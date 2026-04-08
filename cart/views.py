from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddCartItemSerializer
from .permissions import IsCartOwner 

class CartViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    permission_classes = [IsCartOwner] 

class CartItemViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return CartItem.objects.filter(
            cart_id=self.kwargs['cart_pk']
        ).select_related('product') 
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    
    permission_classes = [IsCartOwner]