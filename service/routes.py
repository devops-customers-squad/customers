"""
Customer Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Customer, Address, DataValidationError
from werkzeug.exceptions import NotFound
# Import Flask application
from . import app

######################################################################
# GET Information About the Service
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file("index.html")
    
######################################################################
# UPDATE AN EXISTING CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customers(customer_id):
    """
    Update a Customer
    This endpoint will update a Customer based the body that is posted
    """
    app.logger.info("Request to update Customer with id: %s", customer_id)
    check_content_type("application/json")
    request_data = request.get_json()
    customer = Customer.find(customer_id)
    if not customer:
        raise NotFound("customer with id '{}' was not found.".format(customer_id))
    
    try:
        if "username" in request_data:
            other_customer = Customer.find_by_name(request_data["username"]).first()
            if other_customer is not None and other_customer.id != customer_id:
                message = {
                    "error": "Conflict",
                    "message": "Username '" + request_data["username"] + "' already exists."
                }
                return make_response(
                    jsonify(message), status.HTTP_409_CONFLICT
                ) 
        customer.username = request_data["username"]
        customer.id = customer_id
        customer.first_name = request_data["first_name"]
        customer.last_name = request_data["last_name"]
        customer.password = request_data["password"]
        customer.update()
    except KeyError as error:
        raise DataValidationError(
            "Invalid JSON request body: missing " + error.args[0]
        )
    app.logger.info("customer with ID [%s] updated.", customer.id)
    return make_response(jsonify(customer.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN EXISTING CUSTOMER'S ADDRESS
######################################################################
@app.route("/customers/<int:customer_id>/addresses/<int:address_id>", methods=["PUT"])
def update_customer_addresses(customer_id, address_id):
    """
    Update a Customer's address
    This endpoint will update a Customer's addresses based on the request body.
    """
    app.logger.info("Request to update addresses of Customer with id: %s", customer_id)
    check_content_type("application/json")
    address = Address.find(address_id)
    if not address or address.customer_id != customer_id:
        raise NotFound("address with id '{}' for customer with id '{}' was not found.".format(address_id, customer_id))

    address.deserialize(request.get_json())
    address.address_id = address_id
    address.update()

    app.logger.info("address with ID [%s] for customer with ID [%s] updated.", address.address_id, customer_id)
    return make_response(jsonify(address.serialize()), status.HTTP_200_OK)
    
######################################################################
# ADD A NEW CUSTOMER
######################################################################
@app.route("/customers", methods=["POST"])
def create_customers():
    """
    Creates a Customer
    This endpoint will create a Customer based the data in the body that is posted
    """
    app.logger.info("Request to create a customer")
    check_content_type("application/json")
    customer = Customer()
    customer.deserialize(request.get_json())
    customerfound = Customer.find_by_name(customer.username).first()
    if customerfound:
        message = {
            "error": "Conflict",
            "message": "Username '" + customer.username + "' already exists."
            }
        return make_response(
            jsonify(message), status.HTTP_409_CONFLICT
        ) 
    customer.locked=False
    customer.create()
    message = customer.serialize()
    location_url = url_for("get_customers", customer_id=customer.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# ADD A NEW CUSTOMER ADDRESS
######################################################################
@app.route("/customers/<int:customer_id>/addresses", methods=["POST"])
def create_customer_address(customer_id):
    """
    Creates an Address for the Customer with an id equal to customer_id
    This endpoint will create an Address for the Customer with an id equal
    to the customer_id based the data in the body that is posted
    """  
    app.logger.info("Request to create address for customer with id {}".format(customer_id))
    check_content_type("application/json")
    customer = Customer.find(customer_id)
    if not customer:
        raise NotFound(f"Customer with id '{customer_id}' was not found.")
    address = Address()
    address.deserialize(request.get_json())
    address.customer_id = customer_id
    address.create()
    message = address.serialize()
    location_url = url_for("get_customer_addresses", customer_id = customer.id, 
        address_id = address.address_id, _external = True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )
    
######################################################################
# RETRIEVE A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customers(customer_id):
    """
    Retrieve a single customer
    This endpoint will return a customer based on their id
    """
    app.logger.info(f"Request information for customer with customer_id: {customer_id}")
    customer = Customer.find(customer_id)
    if not customer:
        raise NotFound(f"Customer with id '{customer_id}' was not found.")
    return make_response(jsonify(customer.serialize()), status.HTTP_200_OK)

######################################################################
# RETRIEVE A CUSTOMER ADDRESS
######################################################################
@app.route("/customers/<int:customer_id>/addresses/<int:address_id>", methods=["GET"])
def get_customer_address(customer_id, address_id):
    """
    Retrieve a single customer
    This endpoint will return a customer based on their id
    """
    app.logger.info(f"Request information for customer with customer_id: {customer_id}")
    customer = Customer.find(customer_id)
    if not customer:
        raise NotFound(f"Customer with id '{customer_id}' was not found.")
    address = Address.find(address_id)
    if not address or address.customer_id != customer_id:
        raise NotFound(f"Address with id '{address_id}' belonging to customer with"
            + f" id '{customer_id}' not found")
    return make_response(jsonify(address.serialize()), status.HTTP_200_OK)

######################################################################
# RETRIEVE A CUSTOMER'S ADDRESSES
######################################################################
@app.route("/customers/<int:customer_id>/addresses", methods=["GET"])
def get_customer_addresses(customer_id):
    """
    Retrieve a single customer's addresses
    This endpoint will return a customer's addresses based on the customer's id
    """
    app.logger.info(f"Request addresses for customer with customer_id: {customer_id}")
    customer = Customer.find(customer_id)
    if not customer:
        raise NotFound(f"Customer with id '{customer_id}' was not found.")
    customer_dict = customer.serialize()
    addresses = customer_dict["addresses"]
    if len(request.args) != 0:
      all_query_key = ["city", "state", "country", "zipcode", "street_address"]
      for key in request.args.keys():
        if key not in all_query_key:
          message = {
              "error": "Unsupported key",
              "message": "The query key: '" + key + "' is not supported."
              }

          return make_response(
              jsonify(message), status.HTTP_400_BAD_REQUEST
          ) 

      filter_addresses = []
      for address in addresses:
        found = 0
        for query_key in request.args.keys():
          value = request.args.get(query_key)
          found = 1 if str(address[query_key]) == value else 0
          if not found: break
        if found:  
          filter_addresses.append(address)
     
      addresses = filter_addresses

    return make_response(jsonify(addresses), status.HTTP_200_OK)

######################################################################
# LIST ALL CUSTOMER
######################################################################
@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the customers"""
    app.logger.info("Request for customer list")
    
    all_query_key = ["username", "first_name", "last_name", "prefix_username"]
    for key in request.args.keys():
      if key not in all_query_key:
        message = {
            "error": "Unsupported key",
            "message": "The query key: '" + key + "' is not supported."
            }

        return make_response(
            jsonify(message), status.HTTP_400_BAD_REQUEST
        ) 
    
    username = request.args.get("username")
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    prefix_username = request.args.get("prefix_username")

    def filter(customers1, customers2):
      filter_customers = []
      for cust1 in customers1:
        for cust2 in customers2:
          cust2 = cust2.serialize()
          if cust1['id'] == cust2['id']:
            filter_customers.append(cust1)
            break
      return filter_customers

    customers = Customer.all()
    results = [customer.serialize() for customer in customers]
    if username:
      results = filter(results, Customer.find_by_name(username))
    if first_name:
      results = filter(results, Customer.find_by_first_name(first_name))
    if last_name:
      results = filter(results, Customer.find_by_last_name(last_name))
    if prefix_username:
      results = filter(results, Customer.find_by_prefix_name(prefix_username))

    app.logger.info("Returning %d customers", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# DELETE A CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customers(customer_id):
    """
    Delete a Customer
    This endpoint will delete a Customer based the id specified in the path
    """
    app.logger.info("Request to delete customer with id: %s", customer_id)
    customer = Customer.find(customer_id)
    if customer:
        customer.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# DELETE AN EXISTING CUSTOMER'S ADDRESS
######################################################################
@app.route("/customers/<int:customer_id>/addresses/<int:address_id>", methods=["DELETE"])
def delete_customers_address(customer_id, address_id):
    """
    Delete an existing customer's address
    This endpoint will delete a Customer's address based the customer_id and address_id specified in the path
    """
    app.logger.info("Request to delete address with id: %s, customer with id: %s", address_id, customer_id)
    customer = Customer.find(customer_id)
    if customer:
        address = Address.find(address_id)
        if address: address.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# LOCK AN EXISTING CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>/lock", methods=["PUT"])
def lock_customers(customer_id):
    """
    Lock a Customer
    """
    app.logger.info("Request to lock Customer with id: %s", customer_id)
    check_content_type("application/json")
    customer = Customer.find(customer_id)
    if not customer:
        raise NotFound("customer with id '{}' was not found.".format(customer_id))
    customer.locked = True
    customer.update()
    app.logger.info("customer with ID [%s] is locked.", customer.id)
    return make_response(jsonify(customer.serialize_for_lock()), status.HTTP_200_OK)

######################################################################
# UNLOCK AN EXISTING CUSTOMER
######################################################################
@app.route("/customers/<int:customer_id>/unlock", methods=["PUT"])
def unlock_customers(customer_id):
    """
    Lock a Customer
    """
    app.logger.info("Request to lock Customer with id: %s", customer_id)
    check_content_type("application/json")
    customer = Customer.find(customer_id)
    if not customer:
        raise NotFound("customer with id '{}' was not found.".format(customer_id))
    customer.locked = False
    customer.update()
    app.logger.info("customer with ID [%s] is unlocked.", customer.id)
    return make_response(jsonify(customer.serialize_for_lock()), status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Customer.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be {}".format(content_type))
