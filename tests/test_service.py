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
from unittest.mock import MagicMock, patch

import requests
from flask_api import status    # HTTP Status Codes

from service.models import Wishlist, DB, WishlistProduct
from service.service import app, init_db, initialize_logging, disconnect_db

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:////tmp/test.db')

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
        init_db()

    @classmethod
    def tearDownClass(cls):
        disconnect_db()

    def setUp(self):
        """ Runs before each test """
        DB.drop_all()    # clean up the last tests
        DB.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()

    def test_home(self):
        """ Test the Home Page """
        resp = self.app.get('/home')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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
        self.assertEqual(data[0]['customer_id'], 100)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], "wishlist_name1")
        self.assertEqual(data[1]['customer_id'], 100)
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], "wishlist_name2")
        self.assertEqual(data[2]['customer_id'], 101)
        self.assertEqual(data[2]['id'], 3)
        self.assertEqual(data[2]['name'], "wishlist_name3")
        
    def test_get_wishlist(self):
        """ Test get Wishlist """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.get('/wishlists/%s' % 1)
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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
        resp = self.app.post('/wishlists/12345')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_add_product_to_wishlist(self):
        """ Test adding a product to a wishlist"""
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

        resp2 = self.app.post('/wishlists/1/items', json={
            'product_name': 'macbook'
        }, content_type='application/json')

        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_product(self):
        """ Test getting to a product from a wishlist """
        test_wishlist = Wishlist(name='test', customer_id=1)
        test_wishlist.save()

        test_product = WishlistProduct(wishlist_id=test_wishlist.id, product_id=2,
                                       product_name='macbook')
        test_product.save()
        resp = self.app.get('/wishlists/1/items/2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        product = WishlistProduct()
        product.deserialize(resp.get_json())
        self.assertEqual(product.product_name, 'macbook')
        self.assertEqual(product.wishlist_id, 1)
        self.assertEqual(product.product_id, 2)

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
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['customer_id'], 100)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], "wishlist_name1")

    def test_query_empty_wishlist_by_id(self):
        """ Test querying a empty wishlist by its id """
        resp = self.app.get('/wishlists?id=%s' % 1)
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
        self.assertEqual(data[0]['customer_id'], 100)
        self.assertEqual(data[0]['id'], 2)
        self.assertEqual(data[0]['name'], "wishlist_name2")
        self.assertEqual(data[1]['customer_id'], 101)
        self.assertEqual(data[1]['id'], 3)
        self.assertEqual(data[1]['name'], "wishlist_name2")

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
        self.assertEqual(data[0]['customer_id'], 100)
        self.assertEqual(data[0]['id'], 2)
        self.assertEqual(data[0]['name'], "wishlist_name2")
        self.assertEqual(data[1]['customer_id'], 100)
        self.assertEqual(data[1]['id'], 3)
        self.assertEqual(data[1]['name'], "wishlist_name3")

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
        self.assertEqual(data[0]['customer_id'], 101)
        self.assertEqual(data[0]['id'], 3)
        self.assertEqual(data[0]['name'], "wishlist_name2")

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
        self.assertEqual(data[0]['customer_id'], 100)
        self.assertEqual(data[0]['id'], 2)
        self.assertEqual(data[0]['name'], "wishlist_name2")

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
        self.assertEqual(data[0]['customer_id'], 101)
        self.assertEqual(data[0]['id'], 3)
        self.assertEqual(data[0]['name'], "wishlist_name2")

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
        self.assertEqual(data[0]['customer_id'], 101)
        self.assertEqual(data[0]['id'], 3)
        self.assertEqual(data[0]['name'], "wishlist_name2")


    def test_get_items_in_wishlist(self):
        """ Test getting items from wishlist """
        resp1 = self.app.post('/wishlists', json={
            'name': 'mywishlist',
            'customer_id': 100
        }, content_type='application/json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        first_product = {
            'product_id': 45,
            'product_name': "Rickenbacker 360"
        }
        second_product = {
            'product_id': 22,
            'product_name': "Höfner Bass"
        }

        resp1 = self.app.post('/wishlists/1/items', json=first_product,
                              content_type='application/json')
        resp2 = self.app.post('/wishlists/1/items', json=second_product,
                              content_type='application/json')
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        resp = self.app.get('/wishlists/1/items')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)

        if data[0]['product_id'] != first_product['product_id']:
            first_product, second_product = second_product, first_product

        self.assertEqual(data[0]['product_id'], first_product['product_id'])
        self.assertEqual(data[1]['product_id'], second_product['product_id'])
        self.assertEqual(data[0]['product_name'], first_product['product_name'])
        self.assertEqual(data[1]['product_name'], second_product['product_name'])

    def test_get_items_in_nonexistent_wishlist(self):
        """ Test getting items from a non-existing wishlist """
        resp = self.app.get('/wishlists/123/items')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_items_in_empty_wishlist(self):
        """ Test getting items from an empty wishlist """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        resp = self.app.get('/wishlists/%s/items' % created_wishlist.id)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_from_wishlist(self):
        """ Test deleting a product from a wishlist"""
        test_wishlist = Wishlist(name='test', customer_id=1)
        test_wishlist.save()

        test_product = WishlistProduct(wishlist_id=test_wishlist.id, product_id=2,
                                       product_name='macbook')
        test_product.save()

        resp = self.app.delete('/wishlists/%s/items/%s' %
                               (test_wishlist.id, test_product.product_id),\
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

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
        resp = self.app.get('/wishlists/1/items?product_id=100&product_name=oneitem')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0]['wishlist_id'], 1)
        self.assertEqual(data[0]['product_id'], 100)
        self.assertEqual(data[0]['product_name'], "oneitem")

    def test_query_non_exist_wishlist_item_by_all(self):
        """ Test querying a non existing wishlist item by all of its attribute """
        resp = self.app.post('/wishlists', json={
            'name': 'wishlist_name1',
            'customer_id': 100,
        })
        resp = self.app.get('/wishlists/1/items?product_id=100&product_name=oneitem')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

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
        resp = self.app.get('/wishlists/1/items?product_id=100')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['wishlist_id'], 1)
        self.assertEqual(data[0]['product_id'], 100)
        self.assertEqual(data[0]['product_name'], "oneitem")

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
            'product_id': 102,
            'product_name': 'twoitem'
        })
        resp = self.app.get('/wishlists/1/items?product_name=twoitem')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0]['wishlist_id'], 1)
        self.assertEqual(data[0]['product_id'], 101)
        self.assertEqual(data[0]['product_name'], "twoitem")
        self.assertEqual(data[1]['wishlist_id'], 1)
        self.assertEqual(data[1]['product_id'], 102)
        self.assertEqual(data[1]['product_name'], "twoitem")

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
            'product_id': 102,
            'product_name': 'threeitem'
        })
        resp = self.app.get('/wishlists/1/items')
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0]['wishlist_id'], 1)
        self.assertEqual(data[0]['product_id'], 100)
        self.assertEqual(data[0]['product_name'], "oneitem")
        self.assertEqual(data[1]['wishlist_id'], 1)
        self.assertEqual(data[1]['product_id'], 101)
        self.assertEqual(data[1]['product_name'], "twoitem")
        self.assertEqual(data[2]['wishlist_id'], 1)
        self.assertEqual(data[2]['product_id'], 102)
        self.assertEqual(data[2]['product_name'], "threeitem")

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
                                                        created_wishlist_product.product_id), json={
                                                            'product_name': 'surface_pro'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        wishlist_product = WishlistProduct()
        wishlist_product.deserialize(resp.get_json())
        self.assertEqual(wishlist_product.product_name, 'surface_pro')
        self.assertEqual(wishlist_product.product_id, created_wishlist_product.product_id)
        self.assertEqual(wishlist_product.wishlist_id, created_wishlist_product.wishlist_id)

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
                                                        created_wishlist_product.product_id), json={
                                                        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rename_wishlist_product_different_wishlist(self):
        """ Test renaming a wishlist product when product exists but in a different wishlist """
        created_wishlist1 = Wishlist(customer_id=1, name="name")
        created_wishlist1.save()
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist1.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        resp = self.app.put('/wishlists/%s/items/%s' % (created_wishlist.id,
                                                        created_wishlist_product.product_id), json={
                                                            'product_name': 'surface_pro'})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_rename_wishlist_product_invalid_content_type(self):
        """ Test renaming a wishlist product with invalid content type """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        resp = self.app.put('/wishlists/%s/items/%s' % (created_wishlist.id,
                                                        created_wishlist_product.product_id), json={
                                                            'product_name': 'surface_pro'},
                                                        headers={'content-type': 'text/plain'})
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_remove_all_wishlist(self):
        """ Test removing all items from Wishlist database """
        wishlist1 = Wishlist(customer_id=1, name="name1")
        wishlist1.save()
        wishlist2 = Wishlist(customer_id=1, name="name2")
        wishlist2.save()
        wishistprod1 = WishlistProduct(wishlist_id=wishlist1.id,
                                       product_id=2, product_name='macbook')
        wishistprod1.save()
        resp = self.app.delete('/wishlists/reset')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        resp = self.app.get('/wishlists')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_to_cart_wishlist_not_exist(self):
        """ Test Add to cart when wishlist doesn't exits """
        resp = self.app.put('/wishlists/1/items/1/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_to_cart_product_not_exist(self):
        """ Test Add to cart when wishlist product doesn't exits """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        resp = self.app.put('/wishlists/1/items/1/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_to_cart_product_not_in_wishlist(self):
        """ Test Add to cart when product is not in wishlist """
        created_wishlist = Wishlist(customer_id=1, name="name1")
        created_wishlist.save()
        created_wishlist = Wishlist(customer_id=1, name="name2")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=2,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch('service.models.WishlistProduct.add_to_cart')
    def test_mock_add_to_cart(self, add_to_cart_mock):
        """ Test Add to cart with mock data """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()

        add_to_cart_mock.return_value = None

        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(WishlistProduct.all()), 0)

    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_product_404(self, bad_request_mock):
        """ Test Add to cart when Product in Wishlist but not in Products """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        bad_request_mock.return_value = MagicMock(status_code=404)
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_product_500(self, bad_request_mock):
        """ Test Add to cart Internal service error in either of products call """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        bad_request_mock.return_value = MagicMock(status_code=500)
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_no_price(self, product_request_mock):
        """ Test Add to cart no price returned from Product """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        product_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        product_request_mock.return_value.json.return_value = {
            "id": 2,
            "name": "X's shampoo",
            "stock": 10,
            "description": "This product is very powerful",
            "category": "Health Care"
        }

        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_no_name(self, product_request_mock):
        """ Test Add to cart no name returned from Product """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        product_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        product_request_mock.return_value.json.return_value = {
            "id": 2,
            "stock": 10,
            "price": 20.0,
            "description": "This product is very powerful",
            "category": "Health Care"
        }

        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_product_http_error(self, bad_request_mock):
        """ Test Add to cart HTTPError in product call """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        bad_request_mock.side_effect = requests.exceptions.HTTPError('HTTP Error')
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_product_connection_error(self, bad_request_mock):
        """ Test Add to cart ConnectionError in product call """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        bad_request_mock.side_effect = requests.exceptions.ConnectionError('Connection Error')
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_product_timeout_error(self, bad_request_mock):
        """ Test Add to cart Timeout exception in product call """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        bad_request_mock.side_effect = requests.exceptions.Timeout('Request Timeout')
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_product_request_exception(self, bad_request_mock):
        """ Test Add to cart RequestException in product call """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        bad_request_mock.side_effect = requests.exceptions.RequestException('RequestException')
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_product_unknown_error(self, bad_request_mock):
        """ Test Add to cart Unknown error in product call """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        bad_request_mock.side_effect = Exception('Unknown Exception')
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.ShopCart._add_to_cart')
    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_shopcarts_200(self, product_request_mock, shopcart_request_mock):
        """ Test Add to cart success from ShopCarts - product already exist """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        product_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        product_request_mock.return_value.json.return_value = {
            "id": 2,
            "name": "X's shampoo",
            "stock": 10,
            "price": 20.0,
            "description": "This product is very powerful",
            "category": "Health Care"
        }

        shopcart_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch('service.models.ShopCart._add_to_cart')
    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_shopcarts_201(self, product_request_mock, shopcart_request_mock):
        """ Test Add to cart success from ShopCarts - product added """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        product_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        product_request_mock.return_value.json.return_value = {
            "id": 2,
            "name": "X's shampoo",
            "stock": 10,
            "price": 20.0,
            "description": "This product is very powerful",
            "category": "Health Care"
        }

        shopcart_request_mock.return_value = MagicMock(status_code=status.HTTP_201_CREATED)
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    @patch('service.models.ShopCart._add_to_cart')
    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_shopcarts_500(self, product_request_mock, shopcart_request_mock):
        """ Test Add to cart internal server error from ShopCarts """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        product_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        product_request_mock.return_value.json.return_value = {
            "id": 2,
            "name": "X's shampoo",
            "stock": 10,
            "price": 20.0,
            "description": "This product is very powerful",
            "category": "Health Care"
        }

        shopcart_request_mock.return_value = MagicMock(status_code=
                                                       status.HTTP_500_INTERNAL_SERVER_ERROR)
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.ShopCart._add_to_cart')
    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_shopcarts_http_error(self, product_request_mock,
                                                   shopcart_request_mock):
        """ Test Add to cart raises HTTPError from ShopCarts """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        product_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        product_request_mock.return_value.json.return_value = {
            "id": 2,
            "name": "X's shampoo",
            "stock": 10,
            "price": 20.0,
            "description": "This product is very powerful",
            "category": "Health Care"
        }

        shopcart_request_mock.side_effect = requests.exceptions.HTTPError('HTTP Error')
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.ShopCart._add_to_cart')
    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_shopcarts_connection_error(self, product_request_mock,
                                                         shopcart_request_mock):
        """ Test Add to cart raises ConnectionError from ShopCarts """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        product_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        product_request_mock.return_value.json.return_value = {
            "id": 2,
            "name": "X's shampoo",
            "stock": 10,
            "price": 20.0,
            "description": "This product is very powerful",
            "category": "Health Care"
        }

        shopcart_request_mock.side_effect = requests.exceptions.ConnectionError('Connection Error')
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.ShopCart._add_to_cart')
    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_shopcarts_timeout_error(self, product_request_mock,
                                                      shopcart_request_mock):
        """ Test Add to cart raises Timeout error from ShopCarts """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        product_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        product_request_mock.return_value.json.return_value = {
            "id": 2,
            "name": "X's shampoo",
            "stock": 10,
            "price": 20.0,
            "description": "This product is very powerful",
            "category": "Health Care"
        }

        shopcart_request_mock.side_effect = requests.exceptions.Timeout('Request Timeout')
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.ShopCart._add_to_cart')
    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_shopcarts_request_exception_error(self, product_request_mock,
                                                                shopcart_request_mock):
        """ Test Add to cart raises RequestException from ShopCarts """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        product_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        product_request_mock.return_value.json.return_value = {
            "id": 2,
            "name": "X's shampoo",
            "stock": 10,
            "price": 20.0,
            "description": "This product is very powerful",
            "category": "Health Care"
        }

        shopcart_request_mock.side_effect = requests.exceptions.RequestException('RequestException')
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch('service.models.ShopCart._add_to_cart')
    @patch('service.models.Product._get_product_details')
    def test_mock_add_to_cart_shopcarts_unknown_error(self, product_request_mock,
                                                      shopcart_request_mock):
        """ Test Add to cart raises Unknown error from ShopCarts """
        created_wishlist = Wishlist(customer_id=1, name="name")
        created_wishlist.save()
        created_wishlist_product = WishlistProduct(wishlist_id=created_wishlist.id,
                                                   product_id=2, product_name='macbook')
        created_wishlist_product.save()
        product_request_mock.return_value = MagicMock(status_code=status.HTTP_200_OK)
        product_request_mock.return_value.json.return_value = {
            "id": 2,
            "name": "X's shampoo",
            "stock": 10,
            "price": 20.0,
            "description": "This product is very powerful",
            "category": "Health Care"
        }

        shopcart_request_mock.side_effect = Exception('Unknown Exception')
        resp = self.app.put('/wishlists/1/items/2/add-to-cart')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
