from rest_framework import serializers
from django.db import transaction
from django.db.models import F
from .models import Cart, CartItem
from shop.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    unit_price = serializers.DecimalField(source='product.final_price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta: 
        model = CartItem
        fields = ['id', 'product', 'product_name', 'unit_price', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'grand_total']

    def get_grand_total(self, cart):
        return sum(item.quantity * item.product.final_price for item in cart.items.all())

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Product not found.")
        return value

    @transaction.atomic
    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data.get("quantity", 1)

        cart_item, created = CartItem.objects.get_or_create(
            cart_id=cart_id, 
            product_id=product_id,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity = F('quantity') + quantity
            cart_item.save()
            cart_item.refresh_from_db()
        
        self.instance = cart_item
        return self.instance