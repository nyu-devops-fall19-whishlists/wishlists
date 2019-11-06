"""
Fakes for Product service

"""

import logging
import sys
from flask import Flask, jsonify, make_response
from flask_api import status    # HTTP Status Codes

APP = Flask(__name__)

if not APP.debug:
    print('Setting up logging...')
    # Set up default logging for submodules to use STDOUT
    # datefmt='%m/%d/%Y %I:%M:%S %p'
    FMT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FMT)
    # Make a new log handler that uses STDOUT
    HANDLER = logging.StreamHandler(sys.stdout)
    HANDLER.setFormatter(logging.Formatter(FMT))
    HANDLER.setLevel(logging.INFO)
    # Remove the Flask default handlers and use our own
    HANDLER_LIST = list(APP.logger.handlers)
    for log_handler in HANDLER_LIST:
        APP.logger.removeHandler(log_handler)
    APP.logger.addHandler(HANDLER)
    APP.logger.setLevel(logging.INFO)
    APP.logger.propagate = False
    APP.logger.info('Logging handler established')

@APP.route('/products/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    """ Fake route for getting product details """
    APP.logger.info('Request to get product details of \'%s\'' % product_id)
    return make_response(jsonify({
        "id": product_id,
        "name": "Macbook",
        "stock": 10,
        "price": 1799.0,
        "description": "This product is very powerful",
        "category": "Electronics"
    }), status.HTTP_200_OK)

APP.run(host='0.0.0.0', port=5001)
