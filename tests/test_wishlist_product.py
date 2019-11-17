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
Test cases for WishlistProduct Model
Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os

from service.models import Wishlist, WishlistProduct, DataValidationError, DB
from service import app

DATABASE_URI = os.getenv('DATABASE_URI', \
                        'mysql+pymysql://root:wishlists_dev@0.0.0.0:3306/wishlists')

#######################################################################
#  T E S T   C A S E S
#######################################################################
class TestWishlistProduct(unittest.TestCase):
    """ Test Cases for WishlistProduct """

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
        WishlistProduct.init_db(app)
        DB.drop_all()    # clean up the last tests
        DB.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()

    def test_repr(self):
        """ Create a wishlist product and assert that it exists """
        wishlist_product = WishlistProduct(wishlist_id=123431, product_id=1213321,
                                           product_name="Macbook Pro")
        self.assertTrue(wishlist_product is not None)
        self.assertEqual(repr(wishlist_product), "<Wishlist Product 1213321>")
        self.assertEqual(wishlist_product.wishlist_id, 123431)

    def test_delete_wishlist_product(self):
        """ Delete a Wishlist Product"""
        wishlist = Wishlist(name="wishlist_name", customer_id=1234)
        wishlist.save()
        self.assertEqual(len(wishlist.all()), 1)

        wishlist_product = WishlistProduct(wishlist_id=1, product_id=1213321,
                                           product_name="Macbook Pro")
        wishlist_product.save()
        self.assertTrue(wishlist_product is not None)
        wishlist_product.delete()
        self.assertEqual(len(WishlistProduct.all()), 0)

    def test_deserialize_a_wishlist_product(self):
        """ Test deserialization of a Wishlist product """
        data = {"product_name": "product_name", "wishlist_id": 1234, "product_id": 1}
        product = WishlistProduct()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        # self.assertEqual(product.id, 1)
        self.assertEqual(product.wishlist_id, 1234)
        self.assertEqual(product.product_name, "product_name")
        self.assertEqual(product.product_id, 1)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        product = WishlistProduct()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_missing_data(self):
        """ Test deserialization of missing data """
        data = {"product_name": "product_name"}
        product = WishlistProduct()
        self.assertRaises(DataValidationError, product.deserialize, data)
