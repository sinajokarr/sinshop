from rest_framework import serializers
from .models import Product ,Category ,BaseModel,Comment





class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "image", "price", "discount_percent","final_price"]
        
        
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "product", "user", "text", "rating", "is_approved", "created_at"]
        read_only_fields = ["product", "user", "is_approved", "created_at"]
        
        
        
class ProductDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "sku","description","image", "price", "discount_percent", "final_price", "stock","category","comments" ]
    
        
        
class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    

    class Meta :
        fields = ["id", "name", "slug", "is_active", "product_count"]
        model = Category
        
    def get_product_count(self,obj):
        
        return obj.products.count()
