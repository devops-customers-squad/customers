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
Customers Steps

Steps file for customers.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import requests
from behave import given
from compare import expect

@given('the following customers')
def step_impl(context):
    """ Delete all Customers and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the customers and delete them one by one
    context.resp = requests.get(context.base_url + '/api/customers', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for customer in context.resp.json():
        context.resp = requests.delete(context.base_url + '/api/customers/' + str(customer["id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the database with new customers
    create_url = context.base_url + '/api/customers'
    
    for num_customer, row in enumerate(context.table):
        data = {
            "username": row['username'],
            "password": row['password'],
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            }
        if row["street_address1"] != "None":
            address = [
                        {"street_address": row['street_address1'],
                        "city": row['city1'],
                        "state": row['state1'],
                        "zipcode": row['zipcode1'],
                        "country": row['country1']}
                ]
            data["addresses"] = address
            payload = json.dumps(data)
            context.resp = requests.post(create_url, data=payload, headers=headers)
            if bool(row['several_addresses']) == True and row["street_address2"] != "None":
              context.resp = requests.get(context.base_url + '/api/customers', headers=headers)
              i = 0
              for customer in context.resp.json():
                if num_customer == i:
                  current_customer = customer
                  break
                i += 1
            
              new_address = {"street_address": row['street_address2'],
                        "city": row['city2'],
                        "state": row['state2'],
                        "zipcode": row['zipcode2'],
                        "country": row['country2'],
                        "customer_id": current_customer["id"],
                        "address_id": current_customer["addresses"][0]["address_id"] + 1}

              BASE_API = "{}/{}/addresses".format(create_url, 
                                    str(new_address["customer_id"]))
             
              context.resp = requests.post(BASE_API, data=json.dumps(new_address), headers=headers)
              expect(context.resp.status_code).to_equal(201)
        else:
            data["addresses"] = []
            payload = json.dumps(data)
            context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
       