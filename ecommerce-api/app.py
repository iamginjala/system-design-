from flask import Flask,request,render_template,jsonify,g
from utils import cache,database
from sqlalchemy.exc import SQLAlchemyError
from routes import stocks,order_bp,payment_bp,auth_bp
from graphql_api.schema import schema
from strawberry.flask.views import GraphQLView
import os 
from dotenv import load_dotenv
import time
from utils.logger import get_request_logger,get_error_logger,get_app_logger


load_dotenv()

def create_app():

    app = Flask(__name__)
    app.register_blueprint(stocks)
    app.register_blueprint(order_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(auth_bp)
    logger = get_request_logger()
    

    class CustomGraphQLView(GraphQLView):
        def get_context(self, request, response):
            return {"request": request}

    app.add_url_rule('/graphql', view_func=CustomGraphQLView.as_view("graphql_view", schema=schema))


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
    
    @app.before_request
    def log_request():
        
        logger.info(f"incoming request : {request.method} path: {request.path} IP: {request.remote_addr}")
        g.start_time = time.time()
    
    @app.after_request
    def log_response(response):
        # Use flask.g to store request-specific data (avoids accessing private Request attributes)
        response_time = time.time() - getattr(g, "start_time", time.time())
        response_time_ms = response_time * 1000
        logger.info(f"response for {request.method} {request.path} completed in {response_time_ms:.2f}ms with status {response.status}")
        # logger.info(f"response for {request.method} {request.path} completed in {response_time:.4f}s with status {response.statu0s}")
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        err_logger = get_error_logger()
        err_logger.error(f"exception {e} for {request.method} and path {request.path}",exc_info=True)

        return jsonify({'error': 'Internal server error'}), 500


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
        return render_template('index.html')
    return app


if __name__ == "__main__":
    app = create_app()
    # Use PORT from environment (Render assigns this dynamically)
    port = int(os.getenv('PORT', 5000))
    # Set debug=False in production for security
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)