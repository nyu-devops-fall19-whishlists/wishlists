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
from service.models import Wishlist, db, WishlistProduct
from service.service import app, init_db, initialize_logging

DATABASE_URI = os.getenv('DATABASE_URI', \
                        'mysql+pymysql://root:wishlists_dev@0.0.0.0:3306/wishlists')

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

    def test_list_empty_wishlists(self):
        """ Test listing wishlists if there is no data """
        resp = self.app.get('/wishlists')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_wishlists(self):
        """ Test listing wishlists if there is data """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name3',
            'customer_id': 101,
        })
        resp = self.app.get('/wishlists')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['customer_id'], 100)
        self.assertEqual(data[0][0]['id'], 1)
        self.assertEqual(data[0][0]['name'], "wishlist_name1")
        self.assertEqual(data[0][1]['customer_id'], 100)
        self.assertEqual(data[0][1]['id'], 2)
        self.assertEqual(data[0][1]['name'], "wishlist_name2")
        self.assertEqual(data[0][2]['customer_id'], 101)
        self.assertEqual(data[0][2]['id'], 3)
        self.assertEqual(data[0][2]['name'], "wishlist_name3")

    def test_rename_wishlist(self):
        """ Test renaming a wishlist """
        created_wishlist = Wishlist(customer_id=1, name="oldname")
        created_wishlist.save()
        resp = self.app.put('/wishlists/%s' % created_wishlist.id, json={
            'name': 'newname'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        wishlist = Wishlist()
        wishlist.deserialize(resp.get_json())
        self.assertEqual(wishlist.name, 'newname')
        self.assertEqual(wishlist.customer_id, created_wishlist.customer_id)
        self.assertEqual(wishlist.id, created_wishlist.id)

    def test_rename_wishlist_id_not_found(self):
        """ Test renaming a wishlist when wishlist doesn't exist """
        resp = self.app.put('/wishlists/%s' % 1, json={
            'name': 'newname'
        })
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_rename_wishlist_name_not_provided(self):
        """ Test renaming a wishlist when name is not provided """
        created_wishlist = Wishlist(customer_id=1, name="oldname")
        created_wishlist.save()
        resp = self.app.put('/wishlists/%s' % created_wishlist.id, json={
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rename_wishlist_invalid_content_type(self):
        """ Test renaming a wishlist """
        created_wishlist = Wishlist(customer_id=1, name="oldname")
        created_wishlist.save()
        resp = self.app.put('/wishlists/%s' % created_wishlist.id, json={
            'name': 'newname'
        }, headers={'content-type': 'text/plain'})
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_invalid_operation(self):
        """ Testing invalid HTTP operation """
        created_wishlist = Wishlist(customer_id=1, name="wishlist")
        created_wishlist.save()
        resp = self.app.get('/wishlists/%s' % created_wishlist.id)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_add_product_to_wishlist(self):
        """ Test adding a product to a wishlist"""
        # test_wishlist_product = WishlistProduct(wishlist_id=123, product_id=2)
        test_wishlist = Wishlist(name='test', customer_id=1)
        resp1 = self.app.post('/wishlists', json=test_wishlist.serialize(), content_type='application/json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        test_wishprod = WishlistProduct(wishlist_id=test_wishlist.id, product_id=2, product_name='macbook')
        resp2 = self.app.post('/wishlists/1/items', json=test_wishprod.serialize(), content_type='application/json')
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)

    def test_query_non_existing_product_wishlist(self):
        """ Test getting to a non existing product-wishlist tuple"""
        resp2 = self.app.get('/wishlists/124/items/2')
        self.assertEqual(resp2.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_non_existing_wishlist(self):
        """ Test adding a product in an unexisting wishlist"""
        test_wishprod = WishlistProduct(product_id=2, product_name='macbook')
        resp2 = self.app.post('/wishlists/124/items', json=test_wishprod.serialize(), content_type='application/json')
        self.assertEqual(resp2.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_wishlist_by_id(self):
        """ Test querying a wishlist by its id """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.get('/wishlists?id=%s' % 1)
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0]['customer_id'], 100)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], "wishlist_name1")

    def test_query_empty_wishlist_by_id(self):
        """ Test querying a empty wishlist by its id """
        resp = self.app.get('/wishlists?id=%s' % 1)
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_wishlist_by_name(self):
        """ Test querying a wishlist by name """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 101,
        })
        resp = self.app.get('/wishlists?name=wishlist_name2')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['customer_id'], 100)
        self.assertEqual(data[0][0]['id'], 2)
        self.assertEqual(data[0][0]['name'], "wishlist_name2")
        self.assertEqual(data[0][1]['customer_id'], 101)
        self.assertEqual(data[0][1]['id'], 3)
        self.assertEqual(data[0][1]['name'], "wishlist_name2")

    def test_query_wishlist_by_customer_id(self):
        """ Test querying a wishlist by customer id """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 101,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name3',
            'customer_id': 100,
        })
        resp = self.app.get('/wishlists?customer_id=100')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['customer_id'], 100)
        self.assertEqual(data[0][0]['id'], 2)
        self.assertEqual(data[0][0]['name'], "wishlist_name2")
        self.assertEqual(data[0][1]['customer_id'], 100)
        self.assertEqual(data[0][1]['id'], 3)
        self.assertEqual(data[0][1]['name'], "wishlist_name3")

    def test_query_wishlist_by_name_and_customer_id(self):
        """ Test querying a wishlist by name and customer id """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 101,
        })
        resp = self.app.get('/wishlists?name=wishlist_name2&customer_id=101')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['customer_id'], 101)
        self.assertEqual(data[0][0]['id'], 3)
        self.assertEqual(data[0][0]['name'], "wishlist_name2")

    def test_query_wishlist_by_id_and_customer_id(self):
        """ Test querying a wishlist by id and customer id """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 101,
        })
        resp = self.app.get('/wishlists?id=2&customer_id=100')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['customer_id'], 100)
        self.assertEqual(data[0][0]['id'], 2)
        self.assertEqual(data[0][0]['name'], "wishlist_name2")

    def test_query_wishlist_by_id_and_name(self):
        """ Test querying a wishlist by id and name """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 101,
        })
        resp = self.app.get('/wishlists?id=3&name=wishlist_name2')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['customer_id'], 101)
        self.assertEqual(data[0][0]['id'], 3)
        self.assertEqual(data[0][0]['name'], "wishlist_name2")

    def test_query_wishlist_by_all(self):
        """ Test querying a wishlist by id and name and customer id """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name2',
            'customer_id': 101,
        })
        resp = self.app.get('/wishlists?id=3&name=wishlist_name2&customer_id=101')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['customer_id'], 101)
        self.assertEqual(data[0][0]['id'], 3)
        self.assertEqual(data[0][0]['name'], "wishlist_name2")

    def test_delete_product_from_wishlist(self):
        """ Test deleting a product from a wishlist"""
        test_wishlist = Wishlist(name='test', customer_id=1)
        resp1 = self.app.post('/wishlists', json=test_wishlist.serialize(), content_type='application/json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        test_wishprod = WishlistProduct(wishlist_id=test_wishlist.id, product_id=2, product_name='macbook')
        resp2 = self.app.post('/wishlists/1/items', json=test_wishprod.serialize(), content_type='application/json')
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)

        resp3 = self.app.delete('/wishlists/1/items/1', content_type='application/json')
        self.assertEqual(resp3.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(len(WishlistProduct.all()), 0)
