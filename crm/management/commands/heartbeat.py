import os
from datetime import datetime
from django.core.management.base import BaseCommand
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

class Command(BaseCommand):
    help = 'Log CRM heartbeat message and verify GraphQL endpoint'

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        log_path = '/mnt/c/tmp/crm_heartbeat_log.txt'
        
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            
            try:
                transport = RequestsHTTPTransport(url="http://localhost:8000/graphql/")
                client = Client(transport=transport, fetch_schema_from_transport=True)
                query = gql("query { __schema { queryType { name } } }")
                client.execute(query)
                graphql_status = "GraphQL endpoint responsive"
            except Exception as e:
                graphql_status = f"GraphQL endpoint error: {str(e)}"
            
            with open(log_path, 'a') as log_file:
                log_file.write(f"{timestamp} CRM is alive - {graphql_status}\n")
                
        except Exception as e:
            with open(log_path, 'a') as log_file:
                log_file.write(f"{timestamp} CRM heartbeat error: {str(e)}\n")
