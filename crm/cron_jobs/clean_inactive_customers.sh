#!/bin/bash

# Navigate to the Django project directory
cd "$(dirname "$0")/../.."

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Execute Django management command to clean inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer
import sys

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since one year ago
inactive_customers = Customer.objects.exclude(
    orders__order_date__gte=one_year_ago
).distinct()

# Count before deletion
count = inactive_customers.count()

# Delete inactive customers (suppress Django's verbose output)
if count > 0:
    inactive_customers.delete()

# Print only the count
sys.stdout.write(str(count))
" 2>/dev/null | tail -1)

# Log the result
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers (no orders in last 365 days)" >> /tmp/customer_cleanup_log.txt

# Exit successfully
exit 0
