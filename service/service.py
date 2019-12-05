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
------
GET / - Displays a UI for Selenium testing
GET /wishlists - Returns a list all of the Wishlists
GET /wishlists/{id} - Returns the Properties of the selected Wishlist
GET /wishlists/{id}/items - Returns a list of all Items inside a Wishlist
GET /wishlists/{id}/items/{id} - Returns the Properties of the selected Product
POST /wishlists - creates a new Wishlists record in the database
POST /wishlists/{id}/items - adds a new Product to the Wishlist
PUT /wishlists/{id} - updates a Wishlist record in the database
PUT /wishlists/{id}/items/{id} - updates a Product record in the database
DELETE /wishlists/{id} - deletes a Wishlist record in the database
DELETE /wishlists/{id}/items/{id} - deletes a Product record in the database
PUT /wishlists/{id}/items/{id}/add-to-cart - adds to Cart Product
"""

import atexit
import sys
import logging

from flask import jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from flask_restplus import Api, Resource, fields, reqparse
from werkzeug.exceptions import NotFound

from service.models import Wishlist, WishlistProduct, DataValidationError, DatabaseConnection
# Import Flask application
from . import app


# query string arguments
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument('id', type=str, required=False, help='List Wishlists by id')
wishlist_args.add_argument('name', type=str, required=False, help='List Wishlists by name')
wishlist_args.add_argument('customer_id', type=str, required=False, help='List Wishlists by \
                                                                          customer id')

wishlist_item_args = reqparse.RequestParser()
wishlist_item_args.add_argument('wishlist_id', type=str, required=True, help='List Wishlist Item by Wishlist id')
wishlist_item_args.add_argument('product_id', type=str, required=False, help='List Wishlists Item by Product id')
wishlist_item_args.add_argument('product_name', type=str, required=False, help='List Wishlist Item by \
                                                                          Product name')

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad requests with 400_BAD_REQUEST """
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
# Configure Swagger
######################################################################
api = Api(app,
          version='1.0.0',
          title='Wishlists REST API Service',
          description='This is a sample Wishlist server for an e-commerce website.',
          default='Wishlists',
          default_label='Wishlist operations',
          doc='/apidocs/index.html',
         )

# Define the model so that the docs reflect what can be sent
wishlist_model = api.model('Wishlist', {
    'id': fields.Integer(readOnly=True,
                         required=True,
                         example=1,
                         description='The unique id assigned internally by service'),
    'name': fields.String(required=True,
                          example='Shopping List',
                          description='The name of the Wishlist'),
    'customer_id': fields.Integer(required=True,
                                  min=1,
                                  example=1,
                                  description='The id of the customer that owns the wishlist')
})

create_wishlist_model = api.model('Create Wishlist Request', {
    'name': fields.String(required=True,
                          example='Shopping List',
                          description='The name of the Wishlist'),
    'customer_id': fields.Integer(required=True,
                                  min=1,
                                  example=1,
                                  description='The id of the customer that owns the wishlist')
})

# Define the Wishlist-Product model so that the docs reflect what can be sent
wishlistProduct_model = api.model('WishlistProduct', {
        'wishlist_id': fields.Integer(readOnly=True,
                                  description='Wishlist unique ID'),
    'product_id': fields.Integer(required=True,
                                 description='ID number of the product'),
    'product_name': fields.String(required=True,
                                  description='Name of the product')
                                  })

######################################################################
#  PATH: /wishlists
######################################################################
@api.route('/wishlists', strict_slashes=False)
class WishlistCollection(Resource):
    """ Handles all interactions with collections of Wishlists """

    #------------------------------------------------------------------
    # CREATE WISHLIST
    #------------------------------------------------------------------
    @api.doc('create_wishlists')
    @api.expect(create_wishlist_model)
    @api.response(400, 'Validation errors: "Invalid request: missing name" or \
                  "Invalid request: Wrong customer_id. Expected a number > 0"')
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
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
        # location_url = api.url_for(WishlistResource, wishlist_id=wishlist.id, _external=True)
        location_url = '%s/wishlists/%s' % (request.base_url, wishlist.id)
        return message, status.HTTP_201_CREATED, {'Location': location_url}

    #------------------------------------------------------------------
    # QUERY AND LIST WISHLIST
    #------------------------------------------------------------------
    @api.doc('list_wishlist')
    @api.expect(wishlist_args, validate=True)
    @api.response(404, 'No wishlist found.')
    @api.marshal_list_with(wishlist_model)
    def get(self):
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
            api.abort(404, "No wishlist found.")

        response_content = [res.serialize() for res in wishlist]

        if response_content is None or len(response_content) == 0:
            api.abort(404, "No wishlist found.")

        return response_content, status.HTTP_200_OK

######################################################################
#  PATH: /wishlists/{wishlist_id}
######################################################################
@api.route('/wishlists/<wishlist_id>')
@api.param('wishlist_id', 'The Wishlist identifier')
class WishlistResource(Resource):
    ######################################################################
    # RENAME WISHLIST
    ######################################################################
    @api.doc('rename_wishlist')
    @api.response(404, 'No wishlist found.')
    @api.response(400, 'Validation errors: "Invalid request: missing name"')
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Rename a Wishlist
        This endpoint will return a Wishlist based on it's id
        """
        app.logger.info('Request to rename a wishlist with id: %s', wishlist_id)
        check_content_type('application/json')
        body = request.get_json()
        app.logger.info('Body: %s', body)

        name = body.get('name', '')

        if name == '':
            api.abort(400, "Invalid request: missing name")

        wishlist = Wishlist.find(wishlist_id)

        if not wishlist:
            api.abort(404, "No wishlist found.")

        wishlist.name = name
        wishlist.save()

        return wishlist.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE A WISHLIST
    ######################################################################
    @api.doc('delete_wishlists')
    @api.response(204, 'Wishlist deleted')
    def delete(self, wishlist_id):
        """
        Delete a Wishlist

        This endpoint will delete a Wishlist based the id specified in the path
        """
        app.logger.info('Request to delete wishlist with id: %s', wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()
        return '', status.HTTP_204_NO_CONTENT


######################################################################
# GET INDEX
######################################################################
@app.route('/home')
def index():
    """ Root URL response """
    return app.send_static_file('index.html')

######################################################################
# DELETE ALL WISHLIST DATA (for testing only)
######################################################################
if not app.config['DISABLE_RESET_ENDPOINT']:
    @app.route('/wishlists/reset', methods=['DELETE'])
    def wishlists_reset():
        """ Removes all wishlits and Products from the database """
        DatabaseConnection.reset_db()
        app.logger.info('Request to remove all wishlists from database')
        return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  PATH: /wishlists/{id}/items
######################################################################
@api.route('/wishlists/{id}/items')
class ProductCollection(Resource):
    ######################################################################
    # QUERY AND LIST WISHLIST ITEM
    ######################################################################
    @api.doc('list_wishlist_item')
    @api.expect(wishlist_item_args, validate=True)
    @api.response(404, 'No wishlist item found.')
    @api.marshal_list_with(wishlistProduct_model)
    def get(self):
        """ Query a wishlist items from URL """
        app.logger.info('Querying Wishlist items')
        wishlist_id = request.args.get('wishlist_id')
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(404, "Wishlist was not found.")
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
            api.abort(404, "No wishlist item found.")
        response_content = [res.serialize() for res in wishlist_item]

        if response_content is None or len(response_content) == 0:
            api.abort(404, "No wishlist item found.")

        return response_content, status.HTTP_200_OK

######################################################################
# PATH: /wishlists/{id}/items/{id}
######################################################################
@api.route('/wishlists/<wishlist_id>/items/<product_id>')
@api.param('wishlist_id', 'The Wishlists unique ID number')
@api.param('product_id', 'The Product ID number')
class ProductResource(Resource):
    """
    ProductResource class

    Allows the manipulation of a single Product
    GET /wishlist/{id}/product/{id} - Returns the Product name
    PUT /wishlist/{id}/product/{id} - Update the Product name
    DELETE /wishlist/{id}/product/{id} -  The selected Product from the Wishlist
    """

    #---------------------------------------------------------------------
    # RETRIEVE AN ITEM FROM A WISHLIST
    #---------------------------------------------------------------------
    @api.doc('get_product_details')
    @api.response(404, 'Product not found')
    @api.marshal_with(wishlistProduct_model)
    def get(self, wishlist_id, product_id):
        """
        Retrieve a single Product from a Wishlist
        """
        app.logger.info('Request for {} item in wishlist {}'.format(product_id, wishlist_id))

        wishlist_product = WishlistProduct.find(wishlist_id, product_id)
        if not wishlist_product:
            api.abort(status.HTTP_404_NOT_FOUND, "The wishlist-product tuple ({},{}) you\
                      are looking for was not found.".format(wishlist_id, product_id))
        return wishlist_product.serialize(), status.HTTP_200_OK

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

    location_url = api.url_for(ProductResource, wishlist_id=wishlist.id,
                               product_id=wishlist_product.product_id, _external=True)

    return make_response(jsonify(message), status.HTTP_201_CREATED, {
        'Location': location_url
    })

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
    DatabaseConnection.init()

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

def disconnect_db():
    """ disconnect from the database """
    app.logger.info('Disconnecting from the database')
    DatabaseConnection.disconnect()

atexit.register(disconnect_db)
