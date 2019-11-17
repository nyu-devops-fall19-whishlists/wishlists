# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Wishlist Service

Paths:
-------
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound, InternalServerError

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Wishlist, WishlistProduct, DataValidationError

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST,
                   error='Bad Request',
                   message=message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND,
                   error='Not Found',
                   message=message), status.HTTP_404_NOT_FOUND

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                   error='Method not Allowed',
                   message=message), status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                   error='Unsupported media type',
                   message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   error='Internal Server Error',
                   message=message), status.HTTP_500_INTERNAL_SERVER_ERROR


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return app.send_static_file('index.html')
    # return jsonify(name='Wishlist REST API Service',
    #                version='1.0'), status.HTTP_200_OK

######################################################################
# CREATE WISHLIST
######################################################################
@app.route('/wishlists', methods=['POST'])
def create_wishlist():
    """
    Create a Wishlist
    This endpoint will create a Wishlist. It expects the name and
    customer_id in the body
    """
    app.logger.info('Request to create a wishlist')
    check_content_type('application/json')
    body = request.get_json()
    app.logger.info('Body: %s', body)

    name = body.get('name', '')
    customer_id = body.get('customer_id', 0)

    if name == '':
        raise DataValidationError('Invalid request: missing name')

    if not isinstance(customer_id, int) or customer_id <= 0:
        raise DataValidationError('Invalid request: Wrong customer_id. ' \
                                  'Expected a number > 0')

    wishlist = Wishlist(name=name, customer_id=customer_id)
    wishlist.save()

    message = wishlist.serialize()

    # TO-DO: Replace with URL for GET wishlist once ready
    # url_for('get_wishlist', wishlist_id=wishlist.id, _external=True)
    location_url = '%s/wishlists/%s' % (request.base_url, wishlist.id)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route('/wishlists/<int:wishlist_id>', methods=['DELETE'])
def delete_wishlists(wishlist_id):
    """
    Delete a Wishlist

    This endpoint will delete a Wishlist based the id specified in the path
    """
    app.logger.info('Request to delete wishlist with id: %s', wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# RENAME WISHLIST
######################################################################
@app.route('/wishlists/<int:wishlist_id>', methods=['PUT'])
def rename_wishlist(wishlist_id):
    """
    Rename a Wishlist
    This endpoint will return a Pet based on it's id
    """
    app.logger.info('Request to rename a wishlist with id: %s', wishlist_id)
    check_content_type('application/json')
    body = request.get_json()
    app.logger.info('Body: %s', body)

    name = body.get('name', '')

    if name == '':
        raise DataValidationError('Invalid request: missing name')

    wishlist = Wishlist.find(wishlist_id)

    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))

    wishlist.name = name
    wishlist.save()

    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)

######################################################################
# READ AN EXISTING ITEM FROM WISHLIST
######################################################################
@app.route('/wishlists/<int:wishlist_id>/items/<int:product_id>', methods=['GET'])
def get_a_wishlist_product(wishlist_id, product_id):
    """
    Retrieve a single Product from a Wishlist

    """
    app.logger.info('Request for {} item in wishlist {}'.format(product_id, wishlist_id))


    wishlist_product = WishlistProduct.find(wishlist_id, product_id)
    if not wishlist_product:
        raise NotFound("The wishlist-producttuple ({},{}) you are looking\
                       for was not found.".format(wishlist_id, product_id))
    return make_response(jsonify(wishlist_product.serialize()), status.HTTP_200_OK)

# ######################################################################
# # READ ALL ITMEMS FROM A WISHLIST
# ######################################################################
# @app.route('/wishlists/<int:wishlist_id>/items', methods=['GET'])
# def get_a_product_from_wishlist(wishlist_id):
#     """
#     Retrieve the list of products of a Wishlist
#     """
#     app.logger.info('Request to get all items from wishlist {}'.format(wishlist_id))

#     # checking if the wishlist exists:
#     wishlist = Wishlist.find(wishlist_id)
#     if not wishlist:
#         raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
#     items = []
#     items = WishlistProduct.find_by_wishlist_id(wishlist_id)

#     results = [item.serialize() for item in items]
#     return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# ADD NEW ITEM TO WISHLIST
######################################################################
@app.route('/wishlists/<int:wishlist_id>/items', methods=['POST'])
def add_item(wishlist_id):
    """
    This endpoint adds an item to a Wishlist. It expects the
     wishlist_id and product_id.
    """

    app.logger.info('Request to add item into wishlist')
    check_content_type('application/json')

    # checking if the wishlist exists:
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
    wishlist_product = WishlistProduct()
    wishlist_product.wishlist_id = wishlist_id

    app.logger.info('Request to add {} item to wishlist {}'.format(wishlist_product.product_id,
                                                                   wishlist_id))

    body = request.get_json()
    app.logger.info('Body: %s', body)

    product_name = body.get('product_name', '')
    product_id = body.get('product_id', 0)

    if product_name == '':
        raise DataValidationError('Invalid request: missing name')

    wishlist_product.product_name = product_name

    if product_id == 0:
        raise DataValidationError('Invalid request: missing product id')

    wishlist_product.product_id = product_id

    wishlist_product.save()
    message = wishlist_product.serialize()
    # TO-DO once available: replace URL for READ items on a wishlist
    location_url = url_for('get_a_wishlist_product',
                           wishlist_id=wishlist_product.wishlist_id,
                           product_id=wishlist_product.product_id,
                           _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED, {
        'Location': location_url
    })

######################################################################
# QUERY AND LIST WISHLIST
######################################################################
@app.route('/wishlists', methods=['GET'])
def query_wishlist():
    """ Query a wishlist by its id """
    app.logger.info('Querying Wishlist list')
    wishlist_id = request.args.get('id')
    customer_id = request.args.get('customer_id')
    name = request.args.get('name')
    wishlist = []

    if not wishlist_id and not name and not customer_id:
        wishlist = Wishlist.all()
    else:
        wishlist = Wishlist.find_by_all(wishlist_id=wishlist_id,
                                        customer_id=customer_id, name=name)

    if not wishlist:
        raise NotFound("No wishlist found.")

    response_content = [res.serialize() for res in wishlist]

    if response_content is None or len(response_content) == 0:
        raise NotFound("No wishlist found.")

    return make_response(jsonify(response_content), status.HTTP_200_OK)

######################################################################
# DELETE A WISHLIST PRODUCT
######################################################################
@app.route('/wishlists/<int:wishlist_id>/items/<int:product_id>', methods=['DELETE'])
def delete_wishlists_products(wishlist_id, product_id):
    """
    Delete a Wishlist Product
    This endpoint will delete a Wishlist Product
    """
    app.logger.info('Request to delete wishlist product with id: %s', product_id)
    wishlist_product = WishlistProduct.find(wishlist_id, product_id)
    if wishlist_product:
        wishlist_product.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# QUERY AND LIST WISHLIST ITEM
######################################################################
@app.route('/wishlists/<int:wishlist_id>/items', methods=['GET'])
def query_wishlist_items(wishlist_id):
    """ Query a wishlist items from URL """
    app.logger.info('Querying Wishlist items')
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
    wishlist_id = request.args.get('wishlist_id')
    product_id = request.args.get('product_id')
    product_name = request.args.get('product_name')
    wishlist_item = []

    if not wishlist_id and not product_id and not product_name:
        wishlist_item = WishlistProduct.all()
    else:
        wishlist_item = WishlistProduct.find_by_all(wishlist_id=wishlist_id,
                                                    product_id=product_id,
                                                    product_name=product_name)
    if not wishlist_item:
        raise NotFound("Wishlist item was not found.")
    response_content = [res.serialize() for res in wishlist_item]

    if response_content is None or len(response_content) == 0:
        raise NotFound("Wishlist item was not found.")

    return make_response(jsonify(response_content), status.HTTP_200_OK)

######################################################################
# UPDATE WISHLIST PRODUCT
######################################################################
@app.route('/wishlists/<int:wishlist_id>/items/<int:product_id>', methods=['PUT'])
def rename_wishlist_product(wishlist_id, product_id):
    """
    Update a Wishlist Product
    This endpoint will return a Wishlist Product that is updated
    """
    app.logger.info('Request to update a product with id: %s in wishlist: %s',
                    product_id, wishlist_id)
    check_content_type('application/json')
    body = request.get_json()
    app.logger.info('Body: %s', body)

    product_name = body.get('product_name', '')

    if product_name == '':
        raise DataValidationError('Invalid request: missing name')

    wishlist = Wishlist.find(wishlist_id)

    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))

    wishlist_product = WishlistProduct.find(wishlist_id, product_id)

    if not wishlist_product or wishlist_product.wishlist_id != wishlist_id:
        raise NotFound("Wishlist Product with id '{}' was not found in Wishlist \
                        with id '{}'.".format(product_id, wishlist_id))

    wishlist_product.product_name = product_name
    wishlist_product.save()

    return make_response(jsonify(wishlist_product.serialize()), status.HTTP_200_OK)

######################################################################
# ADD FROM WISHLIST TO CART
######################################################################
@app.route('/wishlists/<int:wishlist_id>/items/<int:product_id>/add-to-cart', methods=['PUT'])
def add_to_cart(wishlist_id, product_id):
    """
    Move item from Wishlist to cart
    """
    app.logger.info('Request to move item %s in wishlist %s to cart', product_id, wishlist_id)

    wishlist = Wishlist.find(wishlist_id)

    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))

    wishlist_product = WishlistProduct.find(wishlist_id, product_id)

    if not wishlist_product or wishlist_product.wishlist_id != wishlist_id:
        raise NotFound("Wishlist Product with id '{}' was not found in Wishlist \
                        with id '{}'.".format(product_id, wishlist_id))

    wishlist_product.add_to_cart(wishlist.customer_id)

    wishlist_product.delete()

    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app  #Needs to be renamed in UPPER_CASE?
    Wishlist.init_db(app)
    WishlistProduct.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print('Setting up logging...')
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.propagate = False
        app.logger.info('Logging handler established')
