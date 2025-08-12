import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Log CRM heartbeat message every 5 minutes and verify GraphQL endpoint"""
    
    # Get current timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # WSL compatible log path
    log_path = '/mnt/c/tmp/crm_heartbeat_log.txt'
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Test GraphQL endpoint responsiveness
        graphql_status = "GraphQL endpoint responsive"
        try:
            transport = RequestsHTTPTransport(url="http://localhost:8000/graphql/")
            client = Client(transport=transport, fetch_schema_from_transport=True)
            
            # Query the schema to test connection
            query = gql("""
            query TestEndpoint {
                __schema {
                    queryType {
                        name
                    }
                }
            }
            """)
            
            result = client.execute(query)
            if result:
                graphql_status = "GraphQL endpoint responsive"
            else:
                graphql_status = "GraphQL endpoint not responding"
                
        except Exception as e:
            graphql_status = f"GraphQL endpoint error: {str(e)}"
        
        # Log the heartbeat message
        heartbeat_message = f"{timestamp} CRM is alive - {graphql_status}\n"
        
        with open(log_path, 'a') as log_file:
            log_file.write(heartbeat_message)
            
    except Exception as e:
        # Fallback logging in case of any issues
        try:
            with open(log_path, 'a') as log_file:
                log_file.write(f"{timestamp} CRM heartbeat error: {str(e)}\n")
        except:
            pass  # Silent fail if even logging fails

def update_low_stock():
    """Update low stock products via GraphQL mutation every 12 hours"""
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # WSL compatible log path
    log_path = '/mnt/c/tmp/low_stock_updates_log.txt'
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql/")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL mutation to update low stock products
        mutation = gql("""
        mutation UpdateLowStock {
            updateLowStockProducts {
                success
                message
                updatedProducts {
                    id
                    name
                    stock
                    price
                }
            }
        }
        """)
        
        # Execute the mutation
        result = client.execute(mutation)
        
        # Process and log results
        mutation_data = result.get('updateLowStockProducts', {})
        success = mutation_data.get('success', False)
        message = mutation_data.get('message', 'No message')
        updated_products = mutation_data.get('updatedProducts', [])
        
        with open(log_path, 'a') as log_file:
            log_file.write(f"\n[{timestamp}] Low Stock Update Job:\n")
            log_file.write(f"[{timestamp}] Status: {message}\n")
            
            if updated_products:
                log_file.write(f"[{timestamp}] Updated Products:\n")
                for product in updated_products:
                    product_name = product.get('name', 'Unknown')
                    new_stock = product.get('stock', 0)
                    price = product.get('price', '0.00')
                    log_file.write(f"[{timestamp}] - {product_name}: Stock updated to {new_stock} (Price: ${price})\n")
            else:
                log_file.write(f"[{timestamp}] No products needed restocking.\n")
        
    except Exception as e:
        # Log errors
        try:
            with open(log_path, 'a') as log_file:
                log_file.write(f"[{timestamp}] ERROR in low stock update: {str(e)}\n")
        except:
            pass  # Silent fail if even logging fails