# E-Commerce API - GraphQL Microservice


[![CI/CD Pipeline](https://github.com/iamginjala/system-design-/actions/workflows/tests.yml/badge.svg)](https://github.com/iamginjala/system-design-/actions/workflows/tests.yml)
[![codecov](https://codecov.io/github/iamginjala/system-design-/graph/badge.svg?token=S5Y14KVETX)](https://codecov.io/github/iamginjala/system-design-)
![Tests: 69 passing](https://img.shields.io/badge/tests-69%20passing-brightgreen)
![Coverage: 91%](https://img.shields.io/badge/coverage-91%25-brightgreen)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)
![Flask](https://img.shields.io/badge/flask-3.0+-black)
![GraphQL](https://img.shields.io/badge/GraphQL-Strawberry-ff69b4)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-336791)
![Redis](https://img.shields.io/badge/redis-7-dc382d)
![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Deployment](https://img.shields.io/badge/deploy-Render.com-46E3B7)
![Status](https://img.shields.io/badge/status-production-success)

A production-ready Flask-based e-commerce API with GraphQL interface, implementing a dual-database architecture for optimal performance.

## Live Demo

**Production URL:** https://ecommerce-api-zafv.onrender.com

**GraphQL Playground:** https://ecommerce-api-zafv.onrender.com/graphql

## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Client[Client Applications]
        Postman[Postman/GraphQL Playground]
    end

    subgraph "Docker Container Network"
        subgraph "Flask Application :5000"
            Flask[Flask App]
            Auth[JWT Authentication]
            Logger[Structured Logging]
            Metrics[Metrics Tracker]

            subgraph "API Layer"
                GraphQL[GraphQL API<br/>Strawberry]
                REST[REST Endpoints<br/>/auth, /health, /metrics]
            end

            subgraph "Business Logic"
                Queries[GraphQL Queries]
                Mutations[GraphQL Mutations]
                RBAC[Role-Based Access Control]
            end
        end

        subgraph "Data Layer"
            Postgres[(PostgreSQL 15<br/>Dynamic Data)]
            Redis[(Redis 7<br/>Cache Layer)]
        end
    end

    subgraph "External Services"
        GitHub[GitHub Actions<br/>CI/CD]
        Render[Render.com<br/>Production Deploy]
    end

    Client --> GraphQL
    Client --> REST
    Postman --> GraphQL
    Postman --> REST

    GraphQL --> Auth
    REST --> Auth
    Auth --> RBAC

    Queries --> Postgres
    Queries --> Redis
    Mutations --> Postgres
    Mutations --> Redis

    GraphQL --> Queries
    GraphQL --> Mutations

    Flask --> Logger
    Flask --> Metrics

    Postgres -.->|Cache<br/>Product Data| Redis
    Redis -.->|60s TTL<br/>Auto-Invalidation| Postgres

    GitHub -->|Push to main| Render
    Render -.->|Auto Deploy| Flask

    style GraphQL fill:#e1f5ff
    style Postgres fill:#336791,color:#fff
    style Redis fill:#dc382d,color:#fff
    style Auth fill:#90EE90
    style RBAC fill:#FFD700
```

### Dual-Database Design

- **PostgreSQL**: Dynamic data (orders, inventory, transactions, users, payments)
- **Redis**: Static data caching (product catalog with 60s TTL, automatic invalidation)

### Tech Stack

- **Backend**: Flask + SQLAlchemy ORM
- **API**: GraphQL (Strawberry) + REST fallback
- **Authentication**: JWT with role-based access control
- **Databases**: PostgreSQL 15, Redis 7
- **Testing**: Pytest (91% coverage, 69 tests)
- **Monitoring**: Structured logging + performance metrics
- **Deployment**: Render.com (Free Tier)
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ ORDERS : creates
    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : "ordered in"
    ORDERS ||--o{ PAYMENTS : has

    USERS {
        uuid user_id PK
        string name
        string email UK
        string password_hash
        string role "customer|admin"
        datetime created_at
        datetime last_login
    }

    PRODUCTS {
        uuid product_id PK
        float price
        int stock_count
        datetime last_updated
    }

    ORDERS {
        uuid order_id PK
        uuid customer_id FK
        float total_amount "Server-calculated"
        string status "pending|confirmed|shipped|delivered"
        string tracking_info
        datetime created_at
        datetime last_updated
    }

    ORDER_ITEMS {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        float price_at_purchase "Immutable snapshot"
    }

    PAYMENTS {
        uuid payment_id PK
        uuid order_id FK
        string customer_id
        float amount
        string currency "Default: INR"
        string payment_method "Default: UPI"
        string payment_status "Pending|Completed|Failed"
        string transaction_id
        datetime created_at
        datetime updated_at
    }
```

### Products Table

- `product_id` (UUID, Primary Key)
- `price` (Float)
- `stock_count` (Integer)
- `last_updated` (DateTime)

### Orders Table

- `order_id` (UUID, Primary Key)
- `customer_id` (String)
- `total_amount` (Float)
- `status` (String)
- `created_at` (DateTime)
- `last_updated` (DateTime)

### Order Items Table

- `id` (UUID, Primary Key)
- `order_id` (UUID, Foreign Key � Orders)
- `product_id` (UUID, Foreign Key � Products)
- `quantity` (Integer)
- `price_at_purchase` (Float)

## Authentication Guide

### Authentication Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant API as Flask API
    participant Auth as JWT Auth
    participant DB as PostgreSQL
    participant GQL as GraphQL Resolver

    Note over C,GQL: Registration Flow
    C->>API: POST /auth/register<br/>{email, password, name}
    API->>API: Validate password<br/>(8+ chars, complexity)
    API->>DB: Check if email exists
    DB-->>API: Email available
    API->>API: Hash password (Werkzeug scrypt)
    API->>DB: INSERT user (role: customer)
    DB-->>API: User created
    API-->>C: 201 Created

    Note over C,GQL: Login Flow
    C->>API: POST /auth/login<br/>{email, password}
    API->>DB: SELECT user WHERE email
    DB-->>API: User record
    API->>API: Verify password hash
    API->>Auth: Generate JWT token<br/>(user_id, name, role)
    Auth-->>API: access_token (24h expiry)
    API-->>C: {access_token, user}

    Note over C,GQL: Authenticated GraphQL Request
    C->>GQL: GraphQL Mutation<br/>Header: Bearer <token>
    GQL->>Auth: Verify JWT token
    Auth->>Auth: Check expiration<br/>Extract user_id & role
    Auth-->>GQL: Token valid, user_id, role
    GQL->>GQL: Check RBAC permissions<br/>(admin vs customer)

    alt Admin operation (e.g., createProduct)
        GQL->>GQL: Require admin role
        alt User is admin
            GQL->>DB: Execute mutation
            DB-->>GQL: Success
            GQL-->>C: Product created
        else User is customer
            GQL-->>C: Error: Admin access required
        end
    else Customer operation (e.g., createOrder)
        GQL->>DB: Execute mutation
        DB-->>GQL: Order created
        GQL-->>C: Order details
    end

    Note over C,GQL: Token Expiration
    C->>GQL: Request after 24h
    GQL->>Auth: Verify token
    Auth-->>GQL: Token expired
    GQL-->>C: 401 Unauthorized<br/>Token has expired
    C->>API: POST /auth/login (re-authenticate)
```

### Overview

This API uses **JWT (JSON Web Token)** authentication for secure access control. Tokens are valid for **24 hours** and include role-based permissions.

**Two User Roles:**
- **Customer**: Can create orders, view their own orders
- **Admin**: Can manage products (create/update/delete), view all orders

### Step 1: Register a New User

Create a new account by sending a POST request to `/auth/register`.

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (@$!%*?&#)

**Example Request:**

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**

```json
{
  "message": "User registered successfully"
}
```

### Step 2: Login to Get JWT Token

Login with your credentials to receive an access token.

**Example Request:**

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "a94102ff-32e3-4240-b251-dd8934065961",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "customer"
  }
}
```

**Important:** Copy the `access_token` - you'll need it for authenticated requests!

### Step 3: Using the JWT Token

Include the token in the `Authorization` header for all authenticated requests.

**Header Format:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example GraphQL Request with Authentication:**

```bash
curl -X POST http://localhost:5000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "query": "mutation { createOrder(input: { items: [{ productId: \"uuid-here\", quantity: 2 }] }) { orderId totalAmount status } }"
  }'
```

**In GraphQL Playground:**

Add to HTTP Headers section:

```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

### Role-Based Access Control

**Customer Permissions:**
- ✅ Create orders
- ✅ View their own orders
- ❌ Create/update/delete products
- ❌ View other customers' orders

**Admin Permissions:**
- ✅ All customer permissions
- ✅ Create/update/delete products
- ✅ View all orders from all customers

**Unauthorized Access Example:**

If a customer tries to create a product:

```json
{
  "errors": [
    {
      "message": "Admin access required",
      "path": ["createProduct"]
    }
  ]
}
```

### Token Expiration

Tokens expire after **24 hours**. When expired, you'll receive:

```json
{
  "errors": [
    {
      "message": "Token has expired",
      "extensions": {
        "code": "UNAUTHORIZED"
      }
    }
  ]
}
```

**Solution:** Login again to get a fresh token.

### Creating an Admin User

By default, new registrations create **customer** accounts. To create an admin:

1. Register normally via `/auth/register`
2. Manually update the database:

```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

(In production, implement a separate admin invitation system)

---

## API Endpoints

### GraphQL Endpoint

All operations through: `/graphql`

**Authentication:** Include `Authorization: Bearer <token>` header for:
- Creating orders
- Viewing orders
- All product mutations (create/update/delete)

### REST Endpoints

- `GET /` - Home page
- `GET /health` - Health check (database + Redis status)
- `GET /metrics` - Performance metrics and statistics
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login and receive JWT token

### Monitoring Endpoints

#### Health Check (`/health`)

Returns system health status including database and cache connectivity.

**Example Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-31T19:26:14.123456",
  "database": "connected",
  "cache": "connected"
}
```

#### Metrics (`/metrics`)

Returns real-time performance metrics and request statistics.

**Example Response:**

```json
{
  "performance": {
    "average_response_time": 75.81,
    "graphql_average_response_time": 58.09
  },
  "requests_by_endpoint": {
    "/auth/login": 3,
    "/auth/register": 2,
    "/graphql": 52,
    "/health": 1,
    "/metrics": 6
  },
  "total_requests": 64,
  "uptime_seconds": 8700.77
}
```

**Metrics Tracked:**
- Average response time (all endpoints)
- GraphQL-specific response time
- Request count per endpoint
- Total requests served
- Server uptime

## Testing with Postman

Pre-configured Postman collections are available in the repository root for easy API testing:

### 📦 Available Collections

**1. Authentication.postman_collection.json**
- Register User
- User Login
- Admin User Login

**2. GraphQL Operations.postman_collection.json**
- Get All Products (No Auth)
- Create Product (Admin)
- Update Product (Admin)
- Delete Product (Admin)
- Create Order (User)
- Get My Orders (User)

### 🚀 How to Use

1. **Download Postman Desktop**: https://www.postman.com/downloads/

2. **Import Collections**:
   - Open Postman
   - Click "Import" button
   - Select both JSON files from the repository root
   - Collections will appear in your sidebar

3. **Set Base URL** (Optional):
   - Create an environment variable `{{baseUrl}}` = `http://localhost:5000`
   - Or use the hardcoded URLs in the collection

4. **Test Workflow**:
   ```
   Step 1: Register User → Get user credentials
   Step 2: User Login → Copy access_token
   Step 3: Use token in Authorization header for other requests
   ```

5. **For Admin Operations**:
   - First create admin user via database:
     ```sql
     UPDATE users SET role = 'admin' WHERE email = 'admin@gmail.com';
     ```
   - Login with admin credentials
   - Use admin token for product mutations

### 💡 Tips

- Start your API first: `docker-compose up -d`
- GraphQL requests use Postman's **GraphQL body type** (not raw JSON)
- Tokens expire after 24 hours - login again if expired
- Check `http://localhost:5000/health` to verify API is running

---

## GraphQL Examples

### Query All Products (No authentication required)

Redis caching enabled with 60-second TTL for optimal performance.

```graphql
query {
  getProducts {
    productId
    price
    stockCount
    lastUpdated
  }
}
```

### Create a Product (Admin only)

**Requires:** `Authorization: Bearer <admin_token>`

```graphql
mutation {
  createProduct(input: { price: 29.99, stockCount: 100 }) {
    productId
    price
    stockCount
    lastUpdated
  }
}
```

### Get Product by ID (No authentication required)

```graphql
query {
  getProductsById(id: "YOUR_PRODUCT_ID") {
    productId
    price
    stockCount
  }
}
```

### Update Product (Admin only)

**Requires:** `Authorization: Bearer <admin_token>`

```graphql
mutation {
  updateProduct(
    input: { productId: "YOUR_PRODUCT_ID", price: 39.99, stockCount: 50 }
  ) {
    productId
    price
    stockCount
  }
}
```

### Create an Order (Authenticated users)

**Requires:** `Authorization: Bearer <user_token>`

Server automatically calculates `totalAmount` and validates stock availability.

```graphql
mutation {
  createOrder(
    input: {
      items: [
        { productId: "YOUR_PRODUCT_ID", quantity: 2 }
        { productId: "ANOTHER_PRODUCT_ID", quantity: 1 }
      ]
    }
  ) {
    orderId
    customerId
    totalAmount
    status
    createdAt
    items {
      productId
      quantity
      priceAtPurchase
    }
  }
}
```

### Query Orders (Role-aware)

**Requires:** `Authorization: Bearer <token>`

- **Customers** see only their own orders
- **Admins** see all orders

```graphql
query {
  getOrders {
    orderId
    customerId
    totalAmount
    status
    createdAt
    items {
      productId
      quantity
      priceAtPurchase
    }
  }
}
```

### Get Order by ID (Authenticated users)

**Requires:** `Authorization: Bearer <token>`

```graphql
query {
  getOrderById(orderId: "YOUR_ORDER_ID") {
    orderId
    totalAmount
    status
    items {
      productId
      quantity
    }
  }
}
```

## Local Development

### Prerequisites

- Docker & Docker Compose
- Python 3.11+

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/iamginjala/system-design-.git
cd system-design-/ecommerce-api
```

2. **Create `.env` file** (use `.env.example` as template)

```bash
DATABASE_URL=postgresql+psycopg2://ecommerce_user:ecommerce_pass@postgres:5432/ecommerce
REDIS_HOST=redis
REDIS_PORT=6379
```

3. **Start services with Docker Compose**

```bash
docker-compose up -d
```

4. **Access the application**

- GraphQL Playground: http://localhost:5000/graphql
- Health Check: http://localhost:5000/health

### Stop Services

```bash
docker-compose down
```

## Deployment

 <!-- CI/CD Pipeline Active -->

### Deploy to Render.com

1. **Create PostgreSQL Database**

   - Instance Type: Free
   - PostgreSQL Version: 15

2. **Create Redis Instance**

   - Instance Type: Free (25MB)

3. **Create Web Service**

   - Connect GitHub repository
   - Root Directory: `ecommerce-api`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python init_db.py && python app.py`

4. **Set Environment Variables**
   - `DATABASE_URL`: (from PostgreSQL instance)
   - `REDIS_URL`: (from Redis instance)

## =

Features

- GraphQL API with Strawberry
- Dual-database architecture (PostgreSQL + Redis)
- Automatic Redis caching for products
- Cache invalidation on updates
- Order management with multiple items
- Server-side price validation (security)
- Docker containerization
- Production deployment on Render
- Automatic database initialization

## Project Structure

```
ecommerce-api/
├── app.py                      # Main Flask application & blueprint registration
├── init_db.py                  # Database initialization script
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Multi-container orchestration
│
├── models/                     # SQLAlchemy ORM models (PostgreSQL)
│   ├── product.py              # Products (price, stock, UUID)
│   ├── order.py                # Orders (customer_id, status, tracking)
│   ├── order_item.py           # OrderItems (junction with price snapshots)
│   ├── user.py                 # Users (JWT auth, role-based)
│   └── payment.py              # Payments (transaction tracking)
│
├── graphql_api/                # GraphQL API layer (Primary interface)
│   ├── schema.py               # Combined schema (Query + Mutation)
│   ├── types.py                # GraphQL types with field descriptions
│   ├── queries.py              # Read operations (with Redis caching)
│   └── mutations.py            # Write operations (admin-authorized)
│
├── routes/                     # REST API endpoints (Fallback)
│   ├── auth.py                 # POST /auth/register, /auth/login
│   ├── products.py             # GET /api/product/<id>
│   ├── orders.py               # GET /api/orders/<id>/track
│   └── payments.py             # POST /api/payments/international
│
├── utils/                      # Utility modules
│   ├── database.py             # PostgreSQL connection & session factory
│   ├── cache.py                # Redis client & caching functions
│   ├── auth.py                 # JWT token generation & verification
│   ├── logger.py               # Structured logging configuration
│   └── metrics.py              # Performance tracking & metrics collection
│
├── tests/                      # Comprehensive test suite (91% coverage)
│   ├── conftest.py             # Pytest fixtures & test configuration
│   ├── test_auth.py            # Authentication tests
│   ├── test_graphql_api.py     # GraphQL operations
│   ├── test_cache.py           # Redis caching
│   ├── test_database.py        # Database operations
│   ├── test_redis.py           # Redis connection
│   ├── test_e2e_flows.py       # End-to-end workflows
│   └── test_edge_cases.py      # Error handling & edge cases
│
├── logs/                       # Application logs (auto-generated)
│   └── app.log                 # Rotating log files
│
└── .github/workflows/
    └── tests.yml               # CI/CD pipeline (tests → deploy)
```

## Security Features

- Server-side price calculation (prevents client manipulation)
- Input validation for all mutations
- UUID-based identifiers
- Environment-based configuration

## Implemented Features

- ✅ JWT authentication with role-based access control
- ✅ User registration with password validation
- ✅ GraphQL API with Strawberry framework
- ✅ Dual-database architecture (PostgreSQL + Redis)
- ✅ Redis caching with automatic invalidation
- ✅ Order management with price snapshots
- ✅ Stock validation and deduction
- ✅ Structured logging system
- ✅ Health check endpoint
- ✅ Performance metrics endpoint
- ✅ Comprehensive test suite (91% coverage, 69 tests)
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Docker containerization

## Future Enhancements

- [ ] Payment gateway integration (Stripe/PayPal)
- [ ] Order workflow automation (pending → confirmed → shipped → delivered)
- [ ] Email notifications (order confirmations, shipping updates)
- [ ] Admin dashboard UI
- [ ] Product search & filtering
- [ ] Pagination for large datasets
- [ ] Rate limiting implementation
- [ ] WebSocket support for real-time updates
- [ ] Production WSGI server (Gunicorn)
- [ ] Monitoring dashboard (Grafana/Prometheus)

## Screenshots

Production deployment screenshots available in `/docs/screenshots/`

## License

MIT

## Author

GitHub: [@iamginjala](https://github.com/iamginjala)
