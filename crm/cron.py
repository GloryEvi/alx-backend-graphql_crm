import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Log CRM heartbeat message every 5 minutes and verify GraphQL endpoint"""
    
    # Get current timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # Windows compatible log path
    log_path = 'C:/tmp/crm_heartbeat_log.txt'
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Test GraphQL endpoint responsiveness
        graphql_status = "GraphQL endpoint responsive"
        try:
            transport = RequestsHTTPTransport(url="http://localhost:8000/graphql/")
            client = Client(transport=transport, fetch_schema_from_transport=True)
            
            # Query the hello field if it exists, otherwise just test connection
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