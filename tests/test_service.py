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
from unittest.mock import MagicMock, patch
from service.models import Wishlist, db, WishlistProduct
from service.service import app, init_db, initialize_logging
from werkzeug.exceptions import NotFound, InternalServerError
from flask import jsonify

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
        """ Test renaming a wishlist with invalid content type """
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
        resp1 = self.app.post('/wishlists', json=test_wishlist.serialize(),
                              content_type='application/json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        test_wishprod = WishlistProduct(product_id=2, product_name='macbook')
        resp2 = self.app.post('/wishlists/1/items', json=test_wishprod.serialize(),
                              content_type='application/json')

        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)

    def test_add_product_to_wishlist_missing_name(self):
        """ Test adding a product without a name to a wishlist """
        test_wishlist = Wishlist(name='test', customer_id=1)
        resp1 = self.app.post('/wishlists', json=test_wishlist.serialize(),
                              content_type='application/json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        resp2 = self.app.post('/wishlists/1/items', json={
            'product_id': 2
        }, content_type='application/json')

        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_product_to_wishlist_missing_product_id(self):
        """ Test adding a product without a product id to a wishlist """
        test_wishlist = Wishlist(name='test', customer_id=1)
        resp1 = self.app.post('/wishlists', json=test_wishlist.serialize(),
                              content_type='application/json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        test_wishprod = WishlistProduct(product_name='macbook')
        resp2 = self.app.post('/wishlists/1/items', json={
            'product_name': 'macbook'
        }, content_type='application/json')

        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_non_existing_product_wishlist(self):
        """ Test getting to a non existing product-wishlist tuple"""
        resp2 = self.app.get('/wishlists/124/items/2')
        self.assertEqual(resp2.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_non_existing_wishlist(self):
        """ Test adding a product in an unexisting wishlist"""
        test_wishprod = WishlistProduct(product_id=2, product_name='macbook')
        resp2 = self.app.post('/wishlists/124/items', json=test_wishprod.serialize(),
                              content_type='application/json')
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
        self.assertEqual(len(data[0]), 1)
        self.assertEqual(data[0][0]['customer_id'], 100)
        self.assertEqual(data[0][0]['id'], 1)
        self.assertEqual(data[0][0]['name'], "wishlist_name1")

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


    def test_get_items_in_wishlist(self):
        """ Test getting items from wishlist """
        resp1 = self.app.post('/wishlists', json={
            'name': 'mywishlist',
            'customer_id': 100
        }, content_type='application/json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        resp1 = self.app.post('/wishlists/1/items', json={
            'product_id': 45,
            'product_name': "Rickenbacker 360"
        }, content_type='application/json')
        resp2 = self.app.post('/wishlists/1/items', json={
            'product_id': 22,
            'product_name': "Höfner Bass"
        }, content_type='application/json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        resp = self.app.get('/wishlists/1/items')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0][0]['product_id'], 45)
        self.assertEqual(data[0][1]['product_id'], 22)
        self.assertEqual(data[0][0]['product_name'], "Rickenbacker 360")
        self.assertEqual(data[0][1]['product_name'], "Höfner Bass")

    def test_get_items_in_nonexistent_wishlist(self):
        """ Test getting items from a non-existing wishlist """
        resp = self.app.get('/wishlists/123/items')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_delete_wishlist(self):
        """ Delete a Wishlist """
        wishlist = Wishlist(name="wishlist_name", customer_id=1234)
        wishlist.save()
        resp = self.app.delete('/wishlists/%s' % wishlist.id)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_wishlist_non_exist(self):
        """ Delete a Wishlist when it doesn't exist """
        resp = self.app.delete('/wishlists/1')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_query_non_exist_wishlist(self):
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
        resp = self.app.get('/wishlists?id=30&name=wishlist_name2&customer_id=101')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_wishlist_item_by_all(self):
        """ Test querying a wishlist item by all of its attribute """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 100,
            'product_name': 'oneitem'
        })
        resp = self.app.get('/wishlists/1/items?id=1&wishlist_id=1&product_id=100&product_name=oneitem')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['id'], 1)
        self.assertEqual(data[0][0]['wishlist_id'], 1)
        self.assertEqual(data[0][0]['product_id'], 100)
        self.assertEqual(data[0][0]['product_name'], "oneitem")

    def test_query_non_exist_wishlist_item_by_all(self):
        """ Test querying a non existing wishlist item by all of its attribute """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.get('/wishlists/1/items?id=1&wishlist_id=1&product_id=100&product_name=oneitem')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_wishlist_item_by_item_id_and_product_name(self):
        """ Test querying a wishlist item by item_id and product_name """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 100,
            'product_name': 'oneitem'
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 101,
            'product_name': 'twoitem'
        })
        resp = self.app.get('/wishlists/1/items?id=2&product_name=twoitem')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['id'], 2)
        self.assertEqual(data[0][0]['wishlist_id'], 1)
        self.assertEqual(data[0][0]['product_id'], 101)
        self.assertEqual(data[0][0]['product_name'], "twoitem")

    def test_query_wishlist_item_by_item_id(self):
        """ Test querying a wishlist item by item_id """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 100,
            'product_name': 'oneitem'
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 101,
            'product_name': 'twoitem'
        })
        resp = self.app.get('/wishlists/1/items?id=2')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['id'], 2)
        self.assertEqual(data[0][0]['wishlist_id'], 1)
        self.assertEqual(data[0][0]['product_id'], 101)
        self.assertEqual(data[0][0]['product_name'], "twoitem")

    def test_query_wishlist_item_by_product_id(self):
        """ Test querying a wishlist item by product id """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 100,
            'product_name': 'oneitem'
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 101,
            'product_name': 'twoitem'
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 100,
            'product_name': 'threeitem'
        })
        resp = self.app.get('/wishlists/1/items?product_id=100')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['id'], 1)
        self.assertEqual(data[0][0]['wishlist_id'], 1)
        self.assertEqual(data[0][0]['product_id'], 100)
        self.assertEqual(data[0][0]['product_name'], "oneitem")
        self.assertEqual(data[0][1]['id'], 3)
        self.assertEqual(data[0][1]['wishlist_id'], 1)
        self.assertEqual(data[0][1]['product_id'], 100)
        self.assertEqual(data[0][1]['product_name'], "threeitem")

    def test_query_wishlist_item_by_product_name(self):
        """ Test querying a wishlist item by product name """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 100,
            'product_name': 'oneitem'
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 101,
            'product_name': 'twoitem'
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 100,
            'product_name': 'twoitem'
        })
        resp = self.app.get('/wishlists/1/items?product_name=twoitem')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['id'], 2)
        self.assertEqual(data[0][0]['wishlist_id'], 1)
        self.assertEqual(data[0][0]['product_id'], 101)
        self.assertEqual(data[0][0]['product_name'], "twoitem")
        self.assertEqual(data[0][1]['id'], 3)
        self.assertEqual(data[0][1]['wishlist_id'], 1)
        self.assertEqual(data[0][1]['product_id'], 100)
        self.assertEqual(data[0][1]['product_name'], "twoitem")

    def test_query_wishlist_item(self):
        """ Test querying all wishlist items """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 100,
            'product_name': 'oneitem'
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 101,
            'product_name': 'twoitem'
        })
        resp = self.app.post('/wishlists/1/items', json={
            'wishlist_id': 1,
            'product_id': 100,
            'product_name': 'twoitem'
        })
        resp = self.app.get('/wishlists/1/items')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0][0]['id'], 1)
        self.assertEqual(data[0][0]['wishlist_id'], 1)
        self.assertEqual(data[0][0]['product_id'], 100)
        self.assertEqual(data[0][0]['product_name'], "oneitem")
        self.assertEqual(data[0][1]['id'], 2)
        self.assertEqual(data[0][1]['wishlist_id'], 1)
        self.assertEqual(data[0][1]['product_id'], 101)
        self.assertEqual(data[0][1]['product_name'], "twoitem")
        self.assertEqual(data[0][2]['id'], 3)
        self.assertEqual(data[0][2]['wishlist_id'], 1)
        self.assertEqual(data[0][2]['product_id'], 100)
        self.assertEqual(data[0][2]['product_name'], "twoitem")

    def test_query_empty_wishlist_item(self):
        """ Test querying all wishlist items from empty item lists"""
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.get('/wishlists/1/items')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_rename_wishlist_product(self):
        """ Test renaming a wishlist product """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                    product_id=2, product_name='macbook')
        created_wishlist_product.save()
        resp = self.app.put('/wishlists/%s/items/%s' % (created_wishlist.id,
                            created_wishlist_product.id), json={
            'product_name': 'surface_pro'
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        wishlist_product = WishlistProduct()
        wishlist_product.deserialize(resp.get_json())
        self.assertEqual(wishlist_product.product_name, 'surface_pro')
        self.assertEqual(wishlist_product.product_id, created_wishlist_product.product_id)
        self.assertEqual(wishlist_product.wishlist_id, created_wishlist_product.wishlist_id)
        self.assertEqual(wishlist_product.id, created_wishlist_product.id)

    def test_rename_wishlist_product_wishlist_not_found(self):
        """ Test renaming a wishlist product when wishlist doesn't exist """
        resp = self.app.put('/wishlists/1/items/1', json={
            'product_name': 'newname'
        })
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_rename_wishlist_product_not_found(self):
        """ Test renaming a wishlist product when product doesn't exist """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        resp = self.app.put('/wishlists/1/items/1', json={
            'product_name': 'newname'
        })
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_rename_wishlist_product_name_not_provided(self):
        """ Test renaming a wishlist product when name is not provided """
        created_wishlist = Wishlist(customer_id=1, name="oldname")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                    product_id=2, product_name='macbook')
        created_wishlist_product.save()
        resp = self.app.put('/wishlists/%s/items/%s' % (created_wishlist.id,
                                                        created_wishlist_product.id), json={
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rename_wishlist_product_different_wishlist(self):
        """ Test renaming a wishlist product """
        created_wishlist1 = Wishlist(customer_id=1, name="name")
        created_wishlist1.save()
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist1.id,
                                    product_id=2, product_name='macbook')
        created_wishlist_product.save()
        resp = self.app.put('/wishlists/%s/items/%s' % (created_wishlist.id,
                            created_wishlist_product.id), json={
            'product_name': 'surface_pro'
        })
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_rename_wishlist_product_invalid_content_type(self):
        """ Test renaming a wishlist product with invalid content type """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                    product_id=2, product_name='macbook')
        created_wishlist_product.save()
        resp = self.app.put('/wishlists/%s/items/%s' % (created_wishlist.id,
                            created_wishlist_product.id), json={
            'product_name': 'surface_pro'
        }, headers={'content-type': 'text/plain'})
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    @patch('service.models.WishlistProduct.add_to_cart')
    def test_mock_add_to_cart(self, add_to_cart_mock):
        """ Test Add to cart with mock data """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                    product_id=2, product_name='macbook')
        created_wishlist_product.save()

        resp = self.app.put('/wishlists/1/items/1/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(WishlistProduct.all()), 0)

    # @patch('service.models.Product.get_product_details')
    # def test_mock_add_to_cart_product_404(self, bad_request_mock):
    #     """ Test a Bad Request error from Add to cart """
    #     created_wishlist = Wishlist(customer_id=1, name="name")
    #     created_wishlist.save()
    #     created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
    #                                 product_id=2, product_name='macbook')
    #     created_wishlist_product.save()
    #     bad_request_mock.return_value = MagicMock(status_code=404)
    #     resp = self.app.put('/wishlists/1/items/1/add-to-cart')
    #     self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # @patch('service.models.Product.get_product_details')
    # def test_mock_add_to_cart_product_500(self, bad_request_mock):
    #     """ Test a Bad Request error from Add to cart """
    #     created_wishlist = Wishlist(customer_id=1, name="name")
    #     created_wishlist.save()
    #     created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
    #                                 product_id=2, product_name='macbook')
    #     created_wishlist_product.save()
    #     bad_request_mock.return_value = MagicMock(status_code=500)
    #     resp = self.app.put('/wishlists/1/items/1/add-to-cart')
    #     self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @patch('service.models.Product.get_product_details')
    # @patch('service.models.ShopCart.add_to_cart')
    # def test_mock_add_to_cart_shopcarts_200(self, shopcart_request_mock):
    #     """ Test a Bad Request error from Add to cart """
    #     created_wishlist = Wishlist(customer_id=1, name="name")
    #     created_wishlist.save()
    #     created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
    #                                 product_id=2, product_name='macbook')
    #     created_wishlist_product.save()
    #     # product_request_mock.return_value = MagicMock(status_code=200, get_json=lambda: jsonify({
    #     #     "id": 2,
    #     #     "name": "X's shampoo",
    #     #     "stock": 10,
    #     #     "price": 20.0,
    #     #     "description": "This product is very powerful",
    #     #     "category": "Health Care"
    #     # }))
    #     shopcart_request_mock = MagicMock(status_code=200)
    #     resp = self.app.put('/wishlists/1/items/1/add-to-cart')
    #     self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    # @patch('service.models.ShopCart.add_to_cart')
    # def test_mock_add_to_cart_shopcarts_500(self, bad_request_mock):
    #     """ Test a Bad Request error from Add to cart """
    #     created_wishlist = Wishlist(customer_id=1, name="name")
    #     created_wishlist.save()
    #     created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
    #                                 product_id=2, product_name='macbook')
    #     created_wishlist_product.save()
    #     bad_request_mock.return_value = MagicMock(status_code=500)
    #     resp = self.app.put('/wishlists/1/items/1/add-to-cart')
    #     self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # @patch('service.models.WishlistProduct.add_to_cart')
    # def test_mock_add_to_cart_product_500(self, bad_request_mock):
    #     """ Test a Bad Request error from Add to cart """
    #     created_wishlist = Wishlist(customer_id=1, name="name")
    #     created_wishlist.save()
    #     created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
    #                                 product_id=2, product_name='macbook')
    #     created_wishlist_product.save()
    #     bad_request_mock.side_effect = NotFound()
    #     resp = self.app.put('/wishlists/1/items/1/add-to-cart')
    #     self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # @patch('service.models.WishlistProduct.add_to_cart')
    # def test_mock_add_to_cart_500(self, bad_request_mock):
    #     """ Test a Internal server error error from Add to cart """
    #     created_wishlist = Wishlist(customer_id=1, name="name")
    #     created_wishlist.save()
    #     created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
    #                                 product_id=2, product_name='macbook')
    #     created_wishlist_product.save()
    #     bad_request_mock.side_effect = InternalServerError()
    #     resp = self.app.put('/wishlists/1/items/1/add-to-cart')
    #     self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
