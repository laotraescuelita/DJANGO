from django.urls import path
from . import views
from .views import ( 
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    delete_products,
    upload_products,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    ItemDetailView,
)

urlpatterns = [
    path('add-to-cart/<int:pk>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:pk>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<int:pk>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('delete_products/', delete_products, name='delete-products'),
    path('upload_products/', upload_products, name='upload-products'),
    path('', ProductListView.as_view(), name='pape-home'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='pape-detail'),
    path('item/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
    path('products/new/', ProductCreateView.as_view(), name='pape-create'),
    path('products/<int:pk>/update', ProductUpdateView.as_view(), name='pape-update'),
    path('products/<int:pk>/delete', ProductDeleteView.as_view(), name='pape-delete'),
    path('search/', views.search_product, name="search"),
    
]
