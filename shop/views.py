from rest_framework import generics , permissions
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Category , Product , Comment
from .serializers import CategorySerializer, ProductDetailSerializer,ProductListSerializer ,CommentSerializer

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        return Category.objects.annotate(
            product_count=Count('products')
        ).filter(is_active=True)
        
         

class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'category': ['exact'], 
        'is_featured': ['exact'],
        'stock': ['gte'], 
        'price': ['gte', 'lte'], 
    }
    
    search_fields = ['name', 'description', 'sku']     
    ordering_fields = ['price', 'created_at']
    
    
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("category").prefetch_related("comments")
    


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_pk')
        serializer.save(user=self.request.user, product_id=product_id)