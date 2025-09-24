from flask import Flask,request,url_for,render_template




core = Flask(__name__)


if __name__ == "__main__":
    core.run(debug=True)