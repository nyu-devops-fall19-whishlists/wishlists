"""
Wishlist Steps

Steps file for wishlist.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
from os import getenv
import logging
import json
import requests
import time
from behave import *
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '60'))

##################################################################
# FUNCTIONS
##################################################################

def get_element_id_from_name(element_name):
    """ Convert an element name to the id of the form field """
    parts = element_name.lower().split(' - ')
    field = parts[0]
    task = parts[1]

    return '_'.join(field.split(' ')) + '_' + ''.join(item[0] for item in task.split(' '))

def get_button_id_from_name(button_name):
    """ Convert a button name to the its id """
    parts = button_name.lower().split(' - ')
    task = parts[0]
    suffix = ''

    if len(parts) > 1:
        resource_type = parts[1]
        suffix = '-' + parts[1][0]

    return task + '-btn' + suffix

def table_contains(element, wishlist_name, customer_id):
    """ Returns true if the results contain a row with the specified wishlist name and customer id """
    rows = element.find_elements(By.TAG_NAME, "tr")
    row_number = -1
    for row in rows:
        row_number += 1
        # Skip the header row
        if row_number == 0:
            continue

        cols = row.find_elements(By.TAG_NAME, "td")
        logging.error(cols)
        if cols[1].text == wishlist_name and cols[2].text == customer_id:
            return True
    return False

##################################################################
# BDD STEPS
##################################################################

@given('The service is running')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/h1'))
    )

@given('the following wishlists')
def step_impl(context):
    """ Delete all Wishlists and load new ones """
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(context.base_url + '/wishlists/reset', headers=headers)
    expect(context.resp.status_code).to_equal(204)
    create_url = context.base_url + '/wishlists'
    for row in context.table:
        data = {
            "customer_id": int(row['customer_id']),
            "name": row['name']
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)

@given('the following products on the first wishlist')
def step_impl(context):
    """ Add one product on each Wishlist """
    headers = {'Content-Type': 'application/json'}
    wishlists_url = context.base_url + '/wishlists'
    id_i = 0
    for row in context.table:
        context.resp = requests.get(wishlists_url)
        wishlist_id = json.loads(context.resp.text)[id_i]['id']
        data = {
            "product_id": int(row['product_id']),
            "product_name": row['product_name']
            }
        payload = json.dumps(data)
        context.resp = requests.post(wishlists_url + '/{}/items'.format(wishlist_id), data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)

@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element((By.XPATH, '/html/body/div/div[1]/h1'), 'Wishlist REST API Service')
    )
    # Uncomment next line to take a screenshot of the web page
    #context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = get_element_id_from_name(element_name)
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = get_element_id_from_name(element_name)
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')

# ##################################################################
# # These two function simulate copy and paste
# ##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = get_element_id_from_name(element_name)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('innerHTML')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = get_element_id_from_name(element_name)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

# ##################################################################
# # This code works because of the following naming convention:
# # The buttons have an id in the html hat is the button text
# # in lowercase followed by '-btn' so the Clean button has an id of
# # id='clear-btn'. That allows us to lowercase the name and add '-btn'
# # to get the element id of any button
# ##################################################################

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = get_button_id_from_name(button)
    context.driver.find_element_by_id(button_id).click()

@when('I press the "{tab}" tab')
def step_impl(context, tab):
    tab_id = ''.join(tab.lower().split(' ')) + '-tab'
    context.driver.find_element_by_id(tab_id).click()

@then('I should see Name = "{wishlist_name}", Customer ID = "{customer_id}" in the results')
def step_impl(context, wishlist_name, customer_id):
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.XPATH, '//div[@id="search_results"]/tr[2]/td[1]'))
    )
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, 'search_results'))
    )
    found = table_contains(element, wishlist_name, customer_id)
    expect(found).to_be(True)

@then('I should see Product ID = "{product_id}", Product Name = "{product_name}" in the results')
def step_impl(context, product_id, product_name):
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.XPATH, '//div[@id="search_results-p"]/tr[2]/td[1]'))
    )
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, 'search_results-p'))
    )
    found = table_contains(element, product_id, product_name)
    expect(found).to_be(True)

@then('I should see "{num_wishlists}" wishlist(s)')
def step_impl(context, num_wishlists):
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.XPATH, '//div[@id="search_results"]/tr[2]/td[1]'))
    )
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, 'search_results'))
    )
    rows = element.find_elements(By.TAG_NAME, "tr")
    expect(len(rows)).to_be(int(num_wishlists) + 1) # +1 for the header

@then('I should see "{num_products}" product(s)')
def step_impl(context, num_products):
    WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.XPATH, '//div[@id="search_results-p"]/tr[2]/td[1]'))
    )
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, 'search_results-p'))
    )
    rows = element.find_elements(By.TAG_NAME, "tr")
    expect(len(rows)).to_be(int(num_products) + 1) # +1 for the header

@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)

@when('I copy the first result')
def step_impl(context):
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.XPATH, '//div[@id="search_results"]/tr[2]/td[1]'))
    )
    context.clipboard = element.get_attribute('innerHTML')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I change "{old_element_name}" to "{new_element_name}"')
def step_impl(context, old_element_name, new_element_name):
    element_id = get_element_id_from_name(old_element_name)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(new_element_name)


@when('I check the items on the first wishlist')
def step_impl(context, wishlist_order):
    """
    Gets all items from the nth wishlist on the database
    """
    wishlists_url = context.base_url + '/wishlists'
    context.resp = requests.get(wishlists_url)
    wishlist_id = json.loads(context.resp.text)[0]['id']
    print(wishlist_id)
    context.resp = requests.get(wishlists_url)
    wishlist_id = json.loads(context.resp.text)[wishlist_order]['id']
    context.resp = requests.get(context.base_url + 'wishlists/{}/items'.format(wishlist_id))
