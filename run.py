from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from app import api
from app.utils.middleware import middleware

app = Flask(__name__)
api.init_app(app)

# app.wsgi_app = middleware(app.wsgi_app)

app.run(host="0.0.0.0", debug=True)
