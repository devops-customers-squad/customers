######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
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
######################################################################

"""
Web Steps

Steps file for web interactions with Silenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
from behave import when, then
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions


def mapping_name(key):
  if key == "Customer ID":
    return "cust_id"
  elif key == "Address ID":
    return "addr_id"
  elif key in set(["Username", "First Name", "Last Name", "Password", "Locked"]):
    return "cust_" + key.lower().replace(" ", "_")
  elif key in set(["Street Address", "Zip", "City", "State", "Country"]):
    return "addr_" + key.lower().replace(" ", "_")
  elif key in set(["Retrieve", "Create Customer", "Update Customer", 
              "Search for Customer", "Query by Username Prefix",
              "Clear All", "Lock", "Unlock", "Delete"]):
    return "cust-" +key.split(" ")[0].lower() +"-btn"
  elif key in set(["Search for Customer Addresses", "Update Customer Address", 
              "Create Customer Address", "Clear Address", "Retrieve Address", "Delete Address"]):
    return "addr-" +key.split(" ")[0].lower() +"-btn"
  else:
    raise "key not in above category"

@when('I visit the "Home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    
   # context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    print(error_msg)
    ensure(message in context.resp.text, False, error_msg)

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = mapping_name(element_name)
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

@when('I set the "{element_name}" to ""')
def step_impl(context, element_name):
    element_id = mapping_name(element_name)
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys("")

@when('I clear the "{element_name}" field')
def step_impl(context, element_name):
    element_id = mapping_name(element_name)
    element = context.driver.find_element_by_id(element_id)
    element.clear()

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = mapping_name(element_name)
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')

@then('the "{element_name}" field should not be empty')
def step_impl(context, element_name):
    element_id = mapping_name(element_name)
    element = context.driver.find_element_by_id(element_id)
    error_msg = "the %s field should not be empty", element_name
    ensure(element.text != u'', False, error_msg)

##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = mapping_name(element_name)
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = mapping_name(element_name)
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = mapping_name(button)
    context.driver.find_element_by_id(button_id).click()

@then('I should see "{name}" in the customer results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'customer_search_results'),
            name
        )
    )
    expect(found).to_be(True)

@then('I should not see "{name}" in the customer results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('customer_search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then('I should see "{name}" in the address results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'address_search_results'),
            name
        )
    )
    expect(found).to_be(True)

@then('I should not see "{name}" in the address results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('address_search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then('I should see 1 row in the address results')
def step_impl(context):
    element = context.driver.find_element_by_id('address_search_results')
    element = element.find_elements_by_tag_name('tr')
    error_msg = "I should see %s row in the address results, but there are %s" % (1, len(element))
    ensure(len(element) -1 == 1, True, error_msg)

@then('I should see {number} rows in the address results')
def step_impl(context, number):
    element = context.driver.find_element_by_id('address_search_results')
    element = element.find_elements_by_tag_name('tr')
    error_msg = "I should see %s rows in the address results, but there are %s" % (number, len(element))
    ensure(len(element) -1 == int(number), True, error_msg)

@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)

##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='customer_username'
# We can then lowercase the name and prefix with customer_ to get the id
##################################################################

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = mapping_name(element_name)
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)

@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = mapping_name(element_name.lower())
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)