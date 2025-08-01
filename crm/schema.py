import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'
        filter_fields = {
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'created_at': ['exact', 'gte', 'lte'],
        }
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'
        filter_fields = {
            'name': ['exact', 'icontains'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
        }
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'
        filter_fields = {
            'total_amount': ['exact', 'gte', 'lte'],
            'order_date': ['exact', 'gte', 'lte'],
            'customer__name': ['exact', 'icontains'],
        }
        interfaces = (graphene.relay.Node,)

# Input Types for Filters
class CustomerFilterInput(graphene.InputObjectType):
    name_icontains = graphene.String()
    email_icontains = graphene.String()
    created_at_gte = graphene.DateTime()
    created_at_lte = graphene.DateTime()
    phone_pattern = graphene.String()

class ProductFilterInput(graphene.InputObjectType):
    name_icontains = graphene.String()
    price_gte = graphene.Float()
    price_lte = graphene.Float()
    stock_gte = graphene.Int()
    stock_lte = graphene.Int()
    low_stock = graphene.Boolean()

class OrderFilterInput(graphene.InputObjectType):
    total_amount_gte = graphene.Float()
    total_amount_lte = graphene.Float()
    order_date_gte = graphene.DateTime()
    order_date_lte = graphene.DateTime()
    customer_name = graphene.String()
    product_name = graphene.String()
    product_id = graphene.Int()

# Input Types for Mutations
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.String(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Mutations 
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            if Customer.objects.filter(email=input.email).exists():
                return CreateCustomer(customer=None, message="Email already exists")
            
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.get('phone', '')
            )
            customer.full_clean()
            customer.save()
            
            return CreateCustomer(customer=customer, message="Customer created successfully")
        except ValidationError as e:
            return CreateCustomer(customer=None, message=f"Validation error: {str(e)}")
        except Exception as e:
            return CreateCustomer(customer=None, message=f"Error: {str(e)}")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)
    
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        created_customers = []
        errors = []
        
        for i, customer_data in enumerate(input):
            try:
                if Customer.objects.filter(email=customer_data.email).exists():
                    errors.append(f"Customer {i+1}: Email {customer_data.email} already exists")
                    continue
                
                customer = Customer(
                    name=customer_data.name,
                    email=customer_data.email,
                    phone=customer_data.get('phone', '')
                )
                customer.full_clean()
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                errors.append(f"Customer {i+1}: {str(e)}")
        
        return BulkCreateCustomers(customers=created_customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            try:
                price = Decimal(input.price)
            except:
                return CreateProduct(product=None, message="Invalid price format")
            
            if price <= 0:
                return CreateProduct(product=None, message="Price must be positive")
            
            stock = input.get('stock', 0)
            if stock < 0:
                return CreateProduct(product=None, message="Stock cannot be negative")
            
            product = Product(
                name=input.name,
                price=price,
                stock=stock
            )
            product.save()
            
            return CreateProduct(product=product, message="Product created successfully")
        except Exception as e:
            return CreateProduct(product=None, message=f"Error: {str(e)}")

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            try:
                customer = Customer.objects.get(pk=input.customer_id)
            except Customer.DoesNotExist:
                return CreateOrder(order=None, message="Invalid customer ID")
            
            if not input.product_ids:
                return CreateOrder(order=None, message="At least one product must be provided")
            
            products = []
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    products.append(product)
                except Product.DoesNotExist:
                    return CreateOrder(order=None, message=f"Invalid product ID: {product_id}")
            
            total_amount = sum(product.price for product in products)
            
            order = Order(
                customer=customer,
                total_amount=total_amount
            )
            order.save()
            order.products.set(products)
            
            return CreateOrder(order=order, message="Order created successfully")
        except Exception as e:
            return CreateOrder(order=None, message=f"Error: {str(e)}")

# Query Class with Filters
class Query(graphene.ObjectType):
    # Connection fields for filtering and pagination
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)
    
    # Basic single object queries
    customer = graphene.Field(CustomerType, id=graphene.Int(required=True))
    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    order = graphene.Field(OrderType, id=graphene.Int(required=True))
    
    # Custom filtered queries with ordering
    customers_filtered = graphene.List(
        CustomerType,
        filter=CustomerFilterInput(),
        order_by=graphene.String()
    )
    products_filtered = graphene.List(
        ProductType,
        filter=ProductFilterInput(),
        order_by=graphene.String()
    )
    orders_filtered = graphene.List(
        OrderType,
        filter=OrderFilterInput(),
        order_by=graphene.String()
    )
    
    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None
    
    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None
    
    def resolve_customers_filtered(self, info, filter=None, order_by=None):
        queryset = Customer.objects.all()
        
        if filter:
            customer_filter = CustomerFilter(filter, queryset=queryset)
            queryset = customer_filter.qs
        
        if order_by:
            queryset = queryset.order_by(order_by)
        
        return queryset
    
    def resolve_products_filtered(self, info, filter=None, order_by=None):
        queryset = Product.objects.all()
        
        if filter:
            product_filter = ProductFilter(filter, queryset=queryset)
            queryset = product_filter.qs
        
        if order_by:
            queryset = queryset.order_by(order_by)
        
        return queryset
    
    def resolve_orders_filtered(self, info, filter=None, order_by=None):
        queryset = Order.objects.all()
        
        if filter:
            order_filter = OrderFilter(filter, queryset=queryset)
            queryset = order_filter.qs
        
        if order_by:
            queryset = queryset.order_by(order_by)
        
        return queryset

# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()