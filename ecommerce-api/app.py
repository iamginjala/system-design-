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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_EXPIRATION_HOURS'] = int(os.getenv('JWT_EXPIRATION_HOURS',24))

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
    app.run(host='0.0.0.0',port=5000,debug=True)