# routes.py
from flask import Flask
from .Scraping_controller import fetch_product, filter_proxies

def create_app():
    app = Flask(__name__)

    # Define routes and map them to controller functions
   # app.route('/proxies/filter', methods=['POST' ])(filter_proxies)
    app.route('/product/details', methods=['POST', 'Get'])(fetch_product)

    return app
