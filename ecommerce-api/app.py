from flask import Flask,request,url_for,render_template
from utils import cache,database
from sqlalchemy.exc import SQLAlchemyError
from routes.products import stocks
from routes.orders import order_bp

app = Flask(__name__)
app.register_blueprint(stocks)
app.register_blueprint(order_bp)

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


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)