#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def send_order_reminders():
    """Find and log pending orders from the last 7 days"""
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql/")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL query to get all orders using connection pattern
        query = gql("""
        query GetAllOrders {
            allOrders {
                edges {
                    node {
                        id
                        orderDate
                        customer {
                            email
                            name
                        }
                        totalAmount
                    }
                }
            }
        }
        """)
        
        # Execute the query
        result = client.execute(query)
        
        # Extract orders from connection structure and filter by date
        edges = result.get('allOrders', {}).get('edges', [])
        seven_days_ago_dt = timezone.now() - timedelta(days=7)
        
        orders = []
        for edge in edges:
            order = edge['node']
            order_date_str = order['orderDate']
            # Parse the order date (assuming ISO format)
            from dateutil import parser
            order_date = parser.parse(order_date_str)
            if order_date >= seven_days_ago_dt:
                orders.append(order)
        
        # Process and log results (Windows compatible path)
        log_path = 'C:/tmp/order_reminders_log.txt'
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'a') as log_file:
            log_file.write(f"\n[{timestamp}] Processing {len(orders)} orders from last 7 days:\n")
            
            for order in orders:
                order_id = order['id']
                customer_email = order['customer']['email']
                customer_name = order['customer']['name']
                order_date = order['orderDate']
                total_amount = order['totalAmount']
                
                log_entry = f"[{timestamp}] Order ID: {order_id}, Customer: {customer_name} ({customer_email}), Date: {order_date}, Amount: ${total_amount}\n"
                log_file.write(log_entry)
        
        # Print success message
        print("Order reminders processed!")
        
    except Exception as e:
        # Log errors (Windows compatible path)
        log_path = 'C:/tmp/order_reminders_log.txt'
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'a') as log_file:
            log_file.write(f"[{timestamp}] ERROR: {str(e)}\n")
        
        print(f"Error processing order reminders: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_order_reminders()
