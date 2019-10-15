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
Wishlist Product - The products that are part of a customer's wishlist used in the ecommerce store

Wishlist Product Attributes:
-----------
wishlist_id(integer) - the wishlist id.
product_id (integer) - the product id.


"""
import logging
from flask_sqlalchemy import SQLAlchemy

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
    def find_by_customer_id(cls, customer_id):
        """ Returns all of the wishlists of one customer """
        return cls.query.filter(cls.customer_id == customer_id)

    @classmethod
    def find_by_name(cls, name):
        """ Returns all of the wishlists of one customer """
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_name_and_customer_id(cls, name, customer_id):
        """ Returns all wishlists of the given name and customer id """
        return cls.query.filter(cls.name == name, cls.customer_id == customer_id)

    @classmethod
    def find_by_id_and_customer_id(cls, wishlist_id, customer_id):
        """ Returns all wishlists of the given name and customer id """
        return cls.query.filter(cls.id == wishlist_id, cls.customer_id == customer_id)

    @classmethod
    def find_by_id_and_name(cls, wishlist_id, name):
        """ Returns all wishlists of the given name and customer id """
        return cls.query.filter(cls.id == wishlist_id, cls.name == name)

    @classmethod
    def find_by_all(cls, wishlist_id, name, customer_id):
        """ Returns wishlists of the given id, name, and customer_id """
        return cls.query.filter(cls.id == wishlist_id, cls.customer_id
        == customer_id, cls.name == name)

class WishlistProduct(db.Model):
    """
    Class that represents a Wishlist Product

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger('flask.app')
    app = None

    # Table Schema
    wishlist_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<Wishlist Product %r>' % (self.product_id)

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables
