# E-Commerce API - GraphQL Microservice

A production-ready Flask-based e-commerce API with GraphQL interface, implementing a dual-database architecture for optimal performance.

## Live Demo

**Production URL:** https://ecommerce-api-zafv.onrender.com

**GraphQL Playground:** https://ecommerce-api-zafv.onrender.com/graphql

## Architecture

### Dual-Database Design

- **PostgreSQL**: Dynamic data (orders, inventory, transactions)
- **Redis**: Static data caching (product catalog, session data)

### Tech Stack

- **Backend**: Flask + SQLAlchemy
- **API**: GraphQL (Strawberry)
- **Databases**: PostgreSQL 15, Redis 7
- **Deployment**: Render.com (Free Tier)
- **Containerization**: Docker + Docker Compose

## Database Schema

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

## API Endpoints

### GraphQL Endpoint

All operations through: `/graphql`

### REST Endpoints

- `GET /` - Home page
- `GET /health` - Health check (database + Redis status)

## GraphQL Examples

### Create a Product

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

### Query All Products (with Redis caching)

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

### Get Product by ID

```graphql
query {
  getProductsById(id: "YOUR_PRODUCT_ID") {
    productId
    price
    stockCount
  }
}
```

### Update Product

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

### Create an Order

```graphql
mutation {
  createOrder(
    input: {
      customerId: "a94102ff-32e3-4240-b251-dd8934065961"
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

### Query All Orders

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

### Get Order by ID

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
app.py                  # Main Flask application
init_db.py             # Database initialization
Dockerfile             # Container configuration
docker-compose.yml     # Multi-container setup
requirements.txt       # Python dependencies
models/                # SQLAlchemy models
 product.py
 order.py
 order_item.py
graphql_api/           # GraphQL layer
 schema.py
 types.py
 queries.py
 mutations.py
utils/                 # Utilities
 database.py        # PostgreSQL connection
 cache.py           # Redis connection
```

## Security Features

- Server-side price calculation (prevents client manipulation)
- Input validation for all mutations
- UUID-based identifiers
- Environment-based configuration

## Future Enhancements

- [ ] User authentication & authorization
- [ ] Payment processing integration
- [ ] Inventory management
- [ ] Order tracking system
- [ ] Admin dashboard
- [ ] Rate limiting
- [ ] Production WSGI server (Gunicorn)

## Screenshots

Production deployment screenshots available in `/docs/screenshots/`

## License

MIT

## Author

GitHub: [@iamginjala](https://github.com/iamginjala)
