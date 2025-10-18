from flask import Flask,request
from utils import cache,database
from sqlalchemy.exc import SQLAlchemyError
from routes import stocks,order_bp,payment_bp,auth_bp
from graphql_api.schema import schema
from strawberry.flask.views import GraphQLView
import os 
from dotenv import load_dotenv



app = Flask(__name__)
app.register_blueprint(stocks)
app.register_blueprint(order_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(auth_bp)

class CustomGraphQLView(GraphQLView):
    def get_context(self, request, response):
        return {"request": request}

app.add_url_rule('/graphql', view_func=CustomGraphQLView.as_view("graphql_view", schema=schema))


load_dotenv()

# Validate required environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required for JWT authentication!")

app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_EXPIRATION_HOURS'] = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# Handle Render's PostgreSQL URL format (postgres:// -> postgresql://)
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    os.environ['DATABASE_URL'] = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

@app.route('/health')
def check_health():
    try:
        with database.engine.connect() as connection:
            ans = "connection successful"
    except SQLAlchemyError as e:
        ans =f"connection unsuccessful {e} "
    if cache.test_connection():
        redis_answer = "success"
    else:
        redis_answer = "Unsuccessful"
    
    return f"database connection {ans} and redis connection {redis_answer}"

@app.route("/")
def home():
    return "GraphQL API is running! Visit /graphql to test it."


if __name__ == "__main__":
    # Use PORT from environment (Render assigns this dynamically)
    port = int(os.getenv('PORT', 5000))
    # Set debug=False in production for security
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)