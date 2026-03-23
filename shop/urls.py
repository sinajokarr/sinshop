from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),    
    path('products/', views.ProductListView.as_view(), name='product-list'),    
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:product_pk>/comments/', views.CommentCreateView.as_view(), name='product-comment-create'),
]