import django_filters
from django.db.models import Q
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    # Basic filters
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date range filters
    created_at_gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Custom phone pattern filter
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern')
    
    class Meta:
        model = Customer
        fields = ['name', 'email']
    
    def filter_phone_pattern(self, queryset, name, value):
        """Filter customers with phone numbers starting with specific pattern"""
        return queryset.filter(phone__startswith=value)

class ProductFilter(django_filters.FilterSet):
    # Basic filters
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    # Price range filters
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Stock filters
    stock = django_filters.NumberFilter()
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    
    # Low stock filter 
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    
    class Meta:
        model = Product
        fields = ['name', 'stock']
    
    def filter_low_stock(self, queryset, name, value):
        """Filter products with low stock (less than 10)"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

class OrderFilter(django_filters.FilterSet):
    # Total amount range filters
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    
    # Date range filters
    order_date_gte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='lte')
    
    # Related field filters
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')
    
    # Custom filter for specific product ID
    product_id = django_filters.NumberFilter(method='filter_by_product_id')
    
    class Meta:
        model = Order
        fields = []
    
    def filter_by_product_id(self, queryset, name, value):
        """Filter orders that include a specific product ID"""
        return queryset.filter(products__id=value).distinct()