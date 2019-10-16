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
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound, InternalServerError
from flask_api import status    # HTTP Status Codes

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Wishlist(db.Model):
    """
    Class that represents a Wishlist

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger('flask.app')
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    name = db.Column(db.String(50))

    # Relationship to be added (in order to retreive the items of a wishlist)
    # items = db.relationship('WishlistProduct')

    def __repr__(self):
        return '<Wishlist %r>' % (self.name)

    def save(self):
        """
        Saves a Wishlist to the data store
        """
        Wishlist.logger.info('Saving %s', self.name)
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes a Wishlist from the data store """
        Wishlist.logger.info('Deleting %s', self.name)
        db.session.delete(self)
        db.session.commit()

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
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the wishlists in the database"""
        return cls.query.all()

    @classmethod
    def find(cls, wishlist_id):
        """ Finds a Wishlist by it's ID """
        cls.logger.info('Processing lookup for id %s ...', wishlist_id)
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

class WishlistProduct(db.Model):
    """
    Class that represents a Wishlist Product

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger('flask.app')
    app = None

    # Table Schema
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'),
                            nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(64), nullable=False)
    # product_price = db.Column(db.Numeric(10,2))

    def __repr__(self):
        return '<Wishlist Product %r>' % (self.product_id)

    def save(self):
        """
        Saves a Wishlist/Product in the data store
        """
        WishlistProduct.logger.info('Saving product {} in wishlist {}'.\
                                    format(self.product_id, self.wishlist_id))

        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes a Wishlist Product from the data store """
        WishlistProduct.logger.info('Deleting Product %s', self.id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Wishlist-Product into a dictionary """
        return {"id": self.id, "wishlist_id": self.wishlist_id, "product_id": self.product_id,
                "product_name": self.product_name}
                # "product_price": self.product_price}

    def deserialize(self, data):
        """
        Deserializes a Wishlist/Product from a dictionary
        Args:
            data (dict): A dictionary containing the WishlistProduct data
        """
        try:
            self.id = data['id']
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
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the wishlists products in the database"""
        return cls.query.all()

    @classmethod
    def find(cls, wishprod_id, wishlist_id, product_id):
        """ Retreives a single product in a wishlist """

        cls.logger.info('Processing lookup for product {} in wishlist \
                        {}...'.format(product_id, wishlist_id))
        return cls.query.get(wishprod_id)

    @classmethod
    def find_by_id(cls, wishprod_id):
        """ Retreives a single product in a wishlist """
        cls.logger.info('Processing lookup for wishlist product{}\
                        ...'.format(wishprod_id))
        return cls.query.get(wishprod_id)

    @classmethod
    def find_by_wishlist_id(cls, wishlist_id):
        """ Query that finds Products on a Wishlist """
        cls.logger.info('Processing available query for {} wishlist...'.format(wishlist_id))
        return cls.query.filter(cls.wishlist_id == wishlist_id)

    @classmethod
    def find_by_all(cls, item_id=None, wishlist_id=None, product_id=None, product_name=None):
        """ Returns wishlist item of the given id, wishlist_id, product_id, and product_name """
        queries = []
        if item_id:
            queries.append(cls.id == item_id)

        if wishlist_id:
            queries.append(cls.wishlist_id == wishlist_id)

        if product_id:
            queries.append(cls.product_id == product_id)

        if product_name:
            queries.append(cls.product_name == product_name)

        return cls.query.filter(*queries)

    def add_to_cart(self, customer_id):
        resp_get_product = Product.get_product_details(self.product_id)

        # if resp_get_product.status_code == status.HTTP_404_NOT_FOUND:
        #     raise NotFound("Wishlist Product with id '{}' was not found in Products \
        #                     with id '{}'.".format(self.id, self.wishlist_id))

        # if resp_get_product.status_code != status.HTTP_200_OK:
        #     raise InternalServerError("Internal Server error in processing Add to cart")

        # product_details = resp_get_product.get_json()

        # product_name = product_details.get('name', '')

        # if product_name == '':
        #     raise InternalServerError('Unable to fetch name for product')

        # product_price = product_details.get('price', -1)

        # if product_price == -1:
        #     raise InternalServerError('Unable to fetch price for product')

        resp_add_to_cart = ShopCart.add_to_cart(customer_id, self.product_id, 10.0, "Name")

        if resp_add_to_cart.status_code != status.HTTP_200_OK or resp_add_to_cart.status_code != status.HTTP_201_CREATED:
            raise InternalServerError('Unable to add product to cart')

# class Product():
#     @classmethod
#     def get_product_details(cls, product_id):
#         return app.get('/products/%s' % product_id)

class ShopCart():
    @classmethod
    def add_to_cart(cls, customer_id, product_id, product_price, product_name):
        return app.post('/shopcarts/%s' % customer_id, json={
            'product_id': product_id,
            'customer_id': customer_id,
            'quantity': 1,
            'price': product_price,
            'text': product_name,
        })
