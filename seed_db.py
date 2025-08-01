import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_database():
    print("Seeding database with sample data...")
    
    # Create sample customers
    customers_data = [
        {"name": "John Doe", "email": "john@example.com", "phone": "+1234567890"},
        {"name": "Jane Smith", "email": "jane@example.com", "phone": "123-456-7890"},
        {"name": "Mike Johnson", "email": "mike@example.com", "phone": "+9876543210"},
    ]
    
    customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=data["email"],
            defaults=data
        )
        customers.append(customer)
        if created:
            print(f"Created customer: {customer.name}")
    
    # Create sample products
    products_data = [
        {"name": "MacBook Pro", "price": Decimal("1299.99"), "stock": 15},
        {"name": "iPhone 14", "price": Decimal("899.99"), "stock": 25},
        {"name": "AirPods Pro", "price": Decimal("249.99"), "stock": 50},
        {"name": "iPad Air", "price": Decimal("599.99"), "stock": 20},
    ]
    
    products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(
            name=data["name"],
            defaults=data
        )
        products.append(product)
        if created:
            print(f"Created product: {product.name}")
    
    # Create sample orders
    if customers and products:
        # Order 1: John buys MacBook and AirPods
        order1 = Order.objects.create(
            customer=customers[0],
            total_amount=customers[0].orders.first().calculate_total() if customers[0].orders.exists() else Decimal("1549.98")
        )
        order1.products.set([products[0], products[2]])  
        order1.total_amount = order1.calculate_total()
        order1.save()
        print(f"Created order for {customers[0].name}: ${order1.total_amount}")
        
        # Order 2: Jane buys iPhone and iPad
        order2 = Order.objects.create(
            customer=customers[1],
            total_amount=Decimal("1499.98")
        )
        order2.products.set([products[1], products[3]])  
        order2.total_amount = order2.calculate_total()
        order2.save()
        print(f"Created order for {customers[1].name}: ${order2.total_amount}")
    
    print("Database seeding completed!")

if __name__ == "__main__":
    seed_database()