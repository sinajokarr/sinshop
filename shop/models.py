import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class BaseModel(models.Model):
 
   
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=200, db_index=True) 
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(BaseModel):
    category = models.ManyToManyField(Category, related_name='products')
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    description = models.TextField(blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    
    stock = models.PositiveIntegerField(default=0)
    
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)  

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]
    @property
    def final_price(self):
        if self.discount_percent > 0:
            discount_multiplier = Decimal((100 - self.discount_percent) / 100.0)
            return self.price * discount_multiplier
        return self.price

    @property
    def is_in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name


class Comment(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    
    is_approved = models.BooleanField(default=False) 

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user.phone_number} on {self.product.name}'