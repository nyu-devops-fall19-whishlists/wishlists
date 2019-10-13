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
Wishlist API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import unittest
import os
import logging
import flask
from flask_api import status    # HTTP Status Codes
from service.models import Wishlist, db
from service.service import app, init_db, initialize_logging

DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:wishlists_dev@0.0.0.0:3306/wishlists')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlistServer(unittest.TestCase):
    """ Wishlist Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.debug = False
        initialize_logging(logging.INFO)
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        init_db()
        db.drop_all()    # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_home(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], 'Wishlist REST API Service')
        self.assertEqual(data['version'], '1.0')

    def test_create_wishlist(self):
        """ Test creating a wishlist """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name',
            'customer_id': 100,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        wishlist = Wishlist()
        wishlist.deserialize(resp.get_json())
        self.assertEqual(wishlist.name, 'wishlist_name')
        self.assertEqual(wishlist.customer_id, 100)
        self.assertEqual(wishlist.id, 1)

    def test_create_wishlist_400_missing_name(self):
        """ Test wrong request when creating a wishlist - missing name """
        resp = self.app.post('/wishlists', json={
            'customer_id': 100,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlist_400_missing_customer_id(self):
        """ Test wrong request when creating a wishlist - missing customer id """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name'
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlist_415(self):
        """ Test creating a wishlist with unsupported content type """
        resp = self.app.post('/wishlists', data={
            'name': 'wishlist_name',
            'customer_id': 100,
        }, headers={'content-type': 'text/plain'})
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
