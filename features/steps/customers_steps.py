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
    for row in context.table: 
        data = {
            "username": row['username'],
            "password": row['password'],
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            }
        if row["street_address"] != "None":
            address = [
                        {"street_address": row['street_address'],
                        "city": row['city'],
                        "state": row['state'],
                        "zipcode": row['zipcode'],
                        "country": row['country']}
                ]
            data["addresses"] = address
        else:
            data["addresses"] = []
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
       