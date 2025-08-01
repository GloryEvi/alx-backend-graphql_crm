import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Customer, Product, Order

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.String(required=True)  # Using String to handle decimal properly
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
            # Check email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                return CreateCustomer(customer=None, message="Email already exists")
            
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.get('phone', '')
            )
            customer.full_clean()  # Validates phone format
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
            # Convert and validate price
            try:
                price = Decimal(input.price)
            except:
                return CreateProduct(product=None, message="Invalid price format")
            
            if price <= 0:
                return CreateProduct(product=None, message="Price must be positive")
            
            # Validate stock
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
            # Validate customer exists
            try:
                customer = Customer.objects.get(pk=input.customer_id)
            except Customer.DoesNotExist:
                return CreateOrder(order=None, message="Invalid customer ID")
            
            # Validate products exist and at least one is provided
            if not input.product_ids:
                return CreateOrder(order=None, message="At least one product must be provided")
            
            products = []
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    products.append(product)
                except Product.DoesNotExist:
                    return CreateOrder(order=None, message=f"Invalid product ID: {product_id}")
            
            # Calculate total amount
            total_amount = sum(product.price for product in products)
            
            # Create order
            order = Order(
                customer=customer,
                total_amount=total_amount
            )
            order.save()
            order.products.set(products)
            
            return CreateOrder(order=order, message="Order created successfully")
        except Exception as e:
            return CreateOrder(order=None, message=f"Error: {str(e)}")

# Query Class
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)
    customer = graphene.Field(CustomerType, id=graphene.Int(required=True))
    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    order = graphene.Field(OrderType, id=graphene.Int(required=True))
    
    def resolve_all_customers(self, info):
        return Customer.objects.all()
    
    def resolve_all_products(self, info):
        return Product.objects.all()
    
    def resolve_all_orders(self, info):
        return Order.objects.all()
    
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

# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()