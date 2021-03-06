from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from app import api

app = Flask(__name__)
api.init_app(app)

# app.wsgi_app = middleware(app.wsgi_app)
if __name__ == "__main__":
	app.run(debug=True)
