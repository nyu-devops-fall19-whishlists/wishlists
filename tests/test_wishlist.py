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
Test cases for Wishlist Model
Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from werkzeug.exceptions import NotFound
from service.models import Wishlist, DataValidationError, db
from service import app

DATABASE_URI = os.getenv('DATABASE_URI', \
                        'mysql+pymysql://root:wishlists_dev@0.0.0.0:3306/wishlists')

#######################################################################
#  T E S T   C A S E S
#######################################################################
class TestWishlist(unittest.TestCase):
    """ Test Cases for Wishlist """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        Wishlist.init_db(app)
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_delete_wishlist(self):
        """ Delete a Wishlist """
        wishlist = Wishlist(name="wishlist_name", customer_id=1234)
        wishlist.save()
        self.assertEqual(len(Wishlist.all()), 1)
        # delete the wishlist and make sure it isn't in the database
        wishlist.delete()
        self.assertEqual(len(Wishlist.all()), 0)

    def test_serialize_a_wishlist(self):
        """ Test serialization of a Wishlist """
        wishlist = Wishlist(name="wishlist_name", customer_id=1234)
        data = wishlist.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "wishlist_name")
        self.assertIn('customer_id', data)
        self.assertEqual(data['customer_id'], 1234)

    def test_deserialize_a_wishlist(self):
        """ Test deserialization of a Wishlist """
        data = {"id": 1, "name": "wishlist_name", "customer_id": 1234}
        wishlist = Wishlist()
        wishlist.deserialize(data)
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist.id, 1)
        self.assertEqual(wishlist.name, "wishlist_name")
        self.assertEqual(wishlist.customer_id, 1234)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_deserialize_missing_data(self):
        """ Test deserialization of missing data """
        data = {"id": 1, "customer_id": 1234}
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_repr(self):
        """ Create a wishlist and assert that it exists """
        wishlist = Wishlist(name="ShoppingList", customer_id=1234)
        self.assertTrue(wishlist is not None)
        self.assertEqual(repr(wishlist), "<Wishlist 'ShoppingList'>")
        self.assertEqual(wishlist.customer_id, 1234)
