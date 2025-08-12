# ALX Backend GraphQL CRM

A comprehensive Django-based Customer Relationship Management (CRM) system with GraphQL API integration, automated maintenance tasks, and health monitoring capabilities.

## Features

- **Customer Management**: Store and manage customer information with email, phone, and contact details
- **Product Catalog**: Manage product inventory with pricing and stock tracking
- **Order Processing**: Handle customer orders with product associations and total calculations
- **GraphQL API**: Modern GraphQL endpoint for flexible data querying and mutations with connection-based pagination
- **Automated Data Cleanup**: Scheduled removal of inactive customers to maintain data hygiene
- **Order Reminder System**: GraphQL-powered order tracking and reminder notifications
- **Health Monitoring**: Automated heartbeat system to monitor CRM and GraphQL endpoint health

## Technology Stack

- **Backend**: Django 5.2
- **API**: GraphQL (using graphene-django with connection pagination)
- **Database**: SQLite3
- **Filtering**: django-filters
- **Task Automation**: django-crontab, Bash scripts, and Django management commands
- **GraphQL Client**: gql library with requests transport
- **Environment**: Cross-platform (Windows/WSL Ubuntu)

## Project Structure

```
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/     # Django project settings
│   ├── settings.py             # Updated with crontab configuration
│   └── ...
├── crm/                         # Main CRM application
│   ├── models.py               # Customer, Product, Order models
│   ├── schema.py               # GraphQL schema with connection pagination
│   ├── filters.py              # Advanced query filtering logic
│   ├── management/             # Custom Django management commands
│   │   └── commands/
│   │       └── heartbeat.py    # Health monitoring command
│   ├── cron_jobs/              # Automated maintenance scripts
│   │   ├── clean_inactive_customers.sh
│   │   ├── customer_cleanup_crontab.txt
│   │   ├── send_order_reminders.py
│   │   └── order_reminders_crontab.txt
│   ├── cron.py                 # Django-crontab heartbeat function
│   └── migrations/             # Database migrations
├── manage.py                   # Django management script
├── db.sqlite3                  # SQLite database with sample data
├── seed_db.py                  # Database seeding script
├── requirements.txt            # Python dependencies (updated)
├── run_heartbeat.bat          # Windows batch file for task scheduler
└── venv_wsl/                  # WSL virtual environment
```

## Models

### Customer
- **Fields**: Name, email (unique), phone number with validation
- **Timestamps**: Created timestamp for tracking
- **Relationships**: One-to-many with orders via foreign key
- **Cleanup**: Automatic removal if no orders in 365 days

### Product  
- **Fields**: Name, price (decimal), stock quantity
- **Timestamps**: Created timestamp
- **Relationships**: Many-to-many with orders
- **Features**: Stock tracking and pricing management

### Order
- **Fields**: Customer association, product associations, total amount, order date
- **Methods**: Automatic total calculation based on associated products
- **GraphQL**: Accessible via connection-based queries with filtering
- **Monitoring**: Tracked for recent activity and reminder systems

## Installation & Setup

### Prerequisites
- Python 3.12+
- WSL Ubuntu (recommended for cron jobs)
- Git

### 1. Clone and Setup
```bash
git clone <repository-url>
cd alx-backend-graphql_crm
```

### 2. Virtual Environment (WSL Ubuntu recommended)
```bash
# Install venv if needed
sudo apt install python3.12-venv

# Create and activate virtual environment
python3 -m venv venv_wsl
source venv_wsl/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Run migrations
python manage.py migrate

# Seed with sample data (optional)
python seed_db.py
```

### 5. Start Development Server
```bash
python manage.py runserver
```

## GraphQL API

### Endpoint
Access the GraphQL interface at: `http://localhost:8000/graphql/`

### Schema Structure
The GraphQL schema includes:

**Queries:**
- `allCustomers` - Customer connection with pagination
- `allProducts` - Product connection with pagination  
- `allOrders` - Order connection with pagination
- `customer(id)` - Single customer by ID
- `product(id)` - Single product by ID
- `order(id)` - Single order by ID
- `customersFiltered` - Advanced customer filtering
- `productsFiltered` - Advanced product filtering
- `ordersFiltered` - Advanced order filtering

**Example Query:**
```graphql
query GetRecentOrders {
  allOrders {
    edges {
      node {
        id
        orderDate
        totalAmount
        customer {
          name
          email
        }
        products {
          edges {
            node {
              name
              price
            }
          }
        }
      }
    }
  }
}
```

## Automated Systems

### 1. Customer Cleanup System

**Purpose**: Remove inactive customers (no orders in 365 days)

**Files:**
- `crm/cron_jobs/clean_inactive_customers.sh`
- `crm/cron_jobs/customer_cleanup_crontab.txt`

**Schedule**: Every Sunday at 2:00 AM
**Logging**: `/tmp/customer_cleanup_log.txt` (Windows: `C:/tmp/`)

**Setup:**
```bash
chmod +x crm/cron_jobs/clean_inactive_customers.sh
crontab crm/cron_jobs/customer_cleanup_crontab.txt
```

### 2. Order Reminder System

**Purpose**: Track and log recent orders (last 7 days) via GraphQL

**Files:**
- `crm/cron_jobs/send_order_reminders.py`
- `crm/cron_jobs/order_reminders_crontab.txt`

**Features:**
- Uses GraphQL client to query order data
- Handles connection-based pagination
- Filters orders by date in Python
- Logs order details with customer information

**Schedule**: Daily at 8:00 AM
**Logging**: `/tmp/order_reminders_log.txt` (Windows: `C:/tmp/`)

**Manual Run:**
```bash
python crm/cron_jobs/send_order_reminders.py
```

### 3. Health Monitoring System

**Purpose**: Monitor CRM and GraphQL endpoint health

**Implementation**: Django management command + django-crontab

**Files:**
- `crm/management/commands/heartbeat.py`
- `crm/cron.py` (django-crontab function)

**Features:**
- Tests GraphQL endpoint connectivity
- Logs timestamp in DD/MM/YYYY-HH:MM:SS format
- Monitors both application and API health
- Cross-platform logging paths

**Schedule**: Every 5 minutes
**Logging**: `/mnt/c/tmp/crm_heartbeat_log.txt` (WSL) or `C:/tmp/` (Windows)

**Setup (WSL Ubuntu):**
```bash
# Add to django-crontab
python manage.py crontab add

# Verify
python manage.py crontab show

# Manual test
python manage.py heartbeat
```

**Log Format:**
```
12/08/2025-00:20:25 CRM is alive - GraphQL endpoint responsive
```

## Development Commands

### Django Management
- **Development server**: `python manage.py runserver`
- **Migrations**: `python manage.py makemigrations && python manage.py migrate`
- **Django shell**: `python manage.py shell`
- **Admin user**: `python manage.py createsuperuser`
- **Heartbeat test**: `python manage.py heartbeat`

### Cron Job Management
- **Add cron jobs**: `python manage.py crontab add`
- **List cron jobs**: `python manage.py crontab show`
- **Remove cron jobs**: `python manage.py crontab remove`

### Log Monitoring
```bash
# Customer cleanup logs
tail -f /tmp/customer_cleanup_log.txt

# Order reminder logs  
tail -f /tmp/order_reminders_log.txt

# Heartbeat logs
tail -f /mnt/c/tmp/crm_heartbeat_log.txt
```

## Dependencies

### Core Requirements
```
Django==5.2.4
graphene-django==3.2.0
django-filter==24.2
django-crontab==0.7.1
gql[requests]==3.5.0
python-dateutil==2.9.0.post0
```

### GraphQL Stack
- **graphene-django**: GraphQL schema definition and server
- **gql**: GraphQL client for automated scripts
- **graphql-core**: Core GraphQL implementation

### Task Management
- **django-crontab**: Django-integrated cron job management
- **python-dateutil**: Date parsing and manipulation

## Environment Notes

### WSL Ubuntu (Recommended)
- Full compatibility with django-crontab
- Native Unix cron job support
- Seamless integration with existing workflows

### Windows
- Alternative batch file approach available
- Windows Task Scheduler integration
- Cross-platform logging paths implemented

## Monitoring and Logs

All automated systems log their activities:

1. **Customer Cleanup**: Tracks deletion counts with timestamps
2. **Order Reminders**: Logs processed orders with customer details  
3. **Health Monitoring**: Continuous GraphQL endpoint status monitoring

Log files are automatically created and maintained in `/tmp/` directory with appropriate permissions.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Ensure all cron jobs are properly configured
5. Update documentation as needed
6. Submit a pull request

## License

This project is part of the ALX Backend program.
