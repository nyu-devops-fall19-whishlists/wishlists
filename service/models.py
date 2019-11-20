# Copyright 2016, 2019 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for Wishlist Service

All of the models are stored in this module

Model
------
Wishlist - A Customer's wishlist used in the ecommerce store

Wishlist Attributes:
-----------
id (integer) - the id of the wishlist.
customer_id (integer) - the id of the customer to whom the wishlist belongs
name (string) - the name of the wishlist.

Model
------
Wishlist Product - The products that are part of a customer's wishlist used in the ecommerce
store

Wishlist Product Attributes:
-------------
wishlist_id(integer) - the wishlist id.
product_id (integer) - the product id.


"""
import logging
import os

import requests
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound, InternalServerError
from flask_api import status    # HTTP Status Codes

from . import app

# Create the SQLAlchemy object to be initialized later in init_db()
DB = SQLAlchemy(app)
logger = logging.getLogger('flask.app')

class DatabaseConnection():
    """ Handles the connection to a database """
    @classmethod
    def init(cls):
        """ Initializes the database session """
        logger.info('Initializing database')
        # This is where we initialize SQLAlchemy from the Flask app
        DB.init_app(app)
        app.app_context().push()
        DB.create_all()  # make our sqlalchemy tables

    @classmethod
    def disconnect(cls):
        """ Disconnect from the database """
        logger.info('Disconnecting from the database')
        DB.session.remove()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Wishlist(DB.Model):
    """
    Class that represents a Wishlist

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    # Table Schema
    id = DB.Column(DB.Integer, primary_key=True)
    customer_id = DB.Column(DB.Integer)
    name = DB.Column(DB.String(50))

    # Relationship to be added (in order to retreive the items of a wishlist)
    # items = DB.relationship('WishlistProduct')

    def __repr__(self):
        return '<Wishlist %r>' % (self.name)

    def save(self):
        """
        Saves a Wishlist to the data store
        """
        logger.info('Saving %s', self.name)
        if not self.id:
            DB.session.add(self)
        DB.session.commit()

    def delete(self):
        """ Removes a Wishlist from the data store """
        logger.info('Deleting %s', self.name)
        DB.session.delete(self)
        DB.session.commit()

    def serialize(self):
        """ Serializes a Wishlist into a dictionary """
        return {"id": self.id,
                "name": self.name,
                "customer_id": self.customer_id}

    def deserialize(self, data):
        """
        Deserializes a Wishlist from a dictionary
        Args:
            data (dict): A dictionary containing the Wishlist data
        """
        try:
            self.id = data['id']
            self.name = data['name']
            self.customer_id = data['customer_id']
        except KeyError as error:
            raise DataValidationError('Invalid wishlist: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid wishlist: body of request contained' \
                                      'bad or no data')
        return self

    @classmethod
    def all(cls):
        """ Returns all of the wishlists in the database"""
        return cls.query.all()

    @classmethod
    def find(cls, wishlist_id):
        """ Finds a Wishlist by it's ID """
        logger.info('Processing lookup for id %s ...', wishlist_id)
        return cls.query.get(wishlist_id)

    @classmethod
    def find_by_all(cls, wishlist_id=None, name=None, customer_id=None):
        """ Returns wishlists of the given id, name, and customer_id """
        queries = []

        if wishlist_id:
            queries.append(cls.id == wishlist_id)

        if customer_id:
            queries.append(cls.customer_id == customer_id)

        if name:
            queries.append(cls.name == name)

        return cls.query.filter(*queries)

    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        # for wishlist in cls.query.all():
        #     DB.session.delete(wishlist)
        # DB.session.commit()
        DB.drop_all()
        DB.create_all()

class WishlistProduct(DB.Model):
    """
    Class that represents a Wishlist Product

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    # Table Schema
    wishlist_id = DB.Column(DB.Integer, DB.ForeignKey('wishlist.id'),
                            nullable=False, primary_key=True)
    product_id = DB.Column(DB.Integer, nullable=False, primary_key=True)
    product_name = DB.Column(DB.String(64), nullable=False)
    # product_price = DB.Column(DB.Numeric(10,2))

    def __repr__(self):
        return '<Wishlist Product %r>' % (self.product_id)

    def save(self):
        """
        Saves a Wishlist Product in the data store
        """
        logger.info('Saving product {} in wishlist {}'.\
                                    format(self.product_id, self.wishlist_id))
        if DB.session.query(WishlistProduct).filter_by(wishlist_id=self.wishlist_id,\
                                                       product_id=self.product_id).count() == 0:
            DB.session.add(self)
        DB.session.commit()

    def delete(self):
        """ Removes a Wishlist Product from the data store """
        logger.info('Deleting Product %s in Wishlist %s',
                                    self.product_id, self.wishlist_id)
        DB.session.delete(self)
        DB.session.commit()

    def serialize(self):
        """ Serializes a Wishlist-Product into a dictionary """

        return {"wishlist_id": self.wishlist_id, "product_id": self.product_id,
                "product_name": self.product_name}
                # "product_price": self.product_price}

    def deserialize(self, data):
        """
        Deserializes a Wishlist/Product from a dictionary
        Args:
            data (dict): A dictionary containing the WishlistProduct data
        """
        try:
            self.wishlist_id = data['wishlist_id']
            self.product_id = data['product_id']
            self.product_name = data['product_name']
            # self.product_price = data['product_price']
        except KeyError as error:
            raise DataValidationError('Invalid Wishlist-Product: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid Wishlist-Product: body of request contained' \
                                      'bad or no data')
        return self

    @classmethod
    def all(cls):
        """ Returns all of the wishlists products in the database"""
        return cls.query.all()

    @classmethod
    def find(cls, wishlist_id, product_id):
        """ Retreives a single product in a wishlist """

        logger.info('Processing lookup for product {} in wishlist \
                        {}...'.format(product_id, wishlist_id))
        return cls.query.get((wishlist_id, product_id))

    @classmethod
    def find_by_all(cls, wishlist_id=None, product_id=None, product_name=None):
        """ Returns wishlist item of the given id, wishlist_id, product_id, and product_name """
        queries = []
        if wishlist_id:
            queries.append(cls.wishlist_id == wishlist_id)

        if product_id:
            queries.append(cls.product_id == product_id)

        if product_name:
            queries.append(cls.product_name == product_name)

        return cls.query.filter(*queries)

    def add_to_cart(self, customer_id):
        """ Adds an item from the wishlist to the cart. Deletes from the wishlist. """
        resp_get_product = Product.get_product_details(self.product_id)

        if resp_get_product.status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound("Product with id '{}' was not found in Wishlist \
                            with id '{}'.".format(self.product_id, self.wishlist_id))

        if resp_get_product.status_code != status.HTTP_200_OK:
            raise InternalServerError("Internal Server error in processing Add to cart")

        product_details = resp_get_product.json()

        product_name = product_details.get('name', '')

        if product_name == '':
            raise InternalServerError('Unable to fetch name for product')

        product_price = product_details.get('price', -1)

        if product_price == -1:
            raise InternalServerError('Unable to fetch price for product')

        resp_add_to_cart = ShopCart.add_to_cart(customer_id, self.product_id, product_price,
                                                product_name)

        if resp_add_to_cart.status_code != status.HTTP_200_OK \
            and resp_add_to_cart.status_code != status.HTTP_201_CREATED:
            raise InternalServerError('Unable to add product to cart')

class Product():
    """Wrapper for all interactions with Product Service"""
    PRODUCT_SERV_URL = os.getenv('PRODUCT_SERV_URL', 'http://127.0.0.1:5001')

    @classmethod
    def _get_product_details(cls, product_id):
        """ Invokes Product service to get product details """
        return requests.get('%s/products/%s' % (cls.PRODUCT_SERV_URL, product_id))

    @classmethod
    def get_product_details(cls, product_id):
        """ Gets Product details """
        try:
            return Product._get_product_details(product_id)
        except requests.exceptions.HTTPError:
            raise InternalServerError("Internal Server error in getting product details")
        except requests.exceptions.ConnectionError:
            raise InternalServerError("Internal Server error in connecing to Products service")
        except requests.exceptions.Timeout:
            raise InternalServerError("Timeout error in connecing to Products service")
        except requests.exceptions.RequestException:
            raise InternalServerError("Internal Server error in getting product details")
        except:
            raise InternalServerError("Internal Server error in getting product details")

class ShopCart():
    """Wrapper for all interactions with ShopCart Service"""
    SHOPCART_SERV_URL = os.getenv('SHOPCART_SERV_URL', 'http://127.0.0.1:5002')

    @classmethod
    def _add_to_cart(cls, customer_id, product_id, product_price, product_name):
        """ Invokes ShopCarts service to add an item from the wishlist to the cart """
        return requests.post('%s/shopcarts/%s' % (cls.SHOPCART_SERV_URL, customer_id), json={
            'product_id': product_id,
            'customer_id': customer_id,
            'quantity': 1,
            'price': product_price,
            'text': product_name,
        })

    @classmethod
    def add_to_cart(cls, customer_id, product_id, product_price, product_name):
        """ Adds an item from the wishlist to the cart """
        try:
            return ShopCart._add_to_cart(customer_id, product_id, product_price, product_name)
        except requests.exceptions.HTTPError:
            raise InternalServerError("Internal Server error in processing Add to cart")
        except requests.exceptions.ConnectionError:
            raise InternalServerError("Internal Server error in connecing to Shopcarts")
        except requests.exceptions.Timeout:
            raise InternalServerError("Timeout error in connecing to ShopCarts")
        except requests.exceptions.RequestException:
            raise InternalServerError("Internal Server error in processing Add to cart")
        except:
            raise InternalServerError("Internal Server error in processing Add to cart")
