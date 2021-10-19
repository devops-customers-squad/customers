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
from service.models import Customer, DataValidationError
from werkzeug.exceptions import NotFound
# Import Flask application
from . import app

######################################################################
# GET Information About the Service
######################################################################
@app.route("/")
def list_services():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Customers REST API Service",
            version="1.0",
            paths=url_for("create_customers", _external=True),
            services=(  "create customer",
                        "add customer",
                        "read customer",
                        "list customers",
                        "update customer",
                        "delete customer",),

            usages=("Uses username, password, firstname, lastname, and addresses to create an new user and returns the result.",
                    "Uses username, password, firstname, lastname, and addresses to add an new user into database and returns the result.",
                    "Finds the customer using a valid customer_id and returns customer's information.",
                    "Updates customer' information and returns the result.",
                    "Deletes a customer and all of its information and returns the result.",
                    )
        ),
        status.HTTP_200_OK,
    )
    
######################################################################
# LIST ALL CUSTOMER
######################################################################
@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the customers"""
    app.logger.info("Request for customer list")
    customers = []
    category = request.args.get("category")
    name = request.args.get("first_name")
   # if category:
    #    customers = Customer.find_by_category(category)
    #elif name:
   #     customers = Customer.find_by_name(name)
   # else:
    #    customers = Customer.all()

    results = [customer.serialize() for customer in customers]

    results = [customer.serialize() for customer in Customer.all()]

    app.logger.info("Returning %d customers", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

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
    customer = Customer.find(customer_id)
    if not customer:
        raise NotFound("customer with id '{}' was not found.".format(customer_id))
    customer.deserialize(request.get_json())
    customer.id = customer_id
    customer.update()

    app.logger.info("customer with ID [%s] updated.", customer.id)
    return make_response(jsonify(customer.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN EXISTING CUSTOMER'S ADDRESSES
######################################################################
@app.route("/customers/<int:customer_id>/addresses", methods=["PUT"])
def update_customer_addresses(customer_id):
    """
    Update a Customer's addresses
    This endpoint will update a Customer's addresses based on the request body.
    """
    app.logger.info("Request to update addresses of Customer with id: %s", customer_id)
    check_content_type("application/json")
    customer = Customer.find(customer_id)
    if not customer:
        raise NotFound("customer with id '{}' was not found.".format(customer_id))

    customer_dict = customer.serialize()
    request_body = request.get_json()

    if not "addresses" in request_body.keys():
        raise DataValidationError(
            "Invalid request body: missing Customer addresses"
        )

    customer_dict["addresses"] = request_body["addresses"]
    customer.deserialize(customer_dict)

    customer.id = customer_id
    customer.update()

    app.logger.info("addresses for customer with ID [%s] updated.", customer.id)
    return make_response(jsonify(customer.serialize()), status.HTTP_200_OK)


######################################################################
# GET Information About the Service
######################################################################
@app.route("/services", methods=["GET"])
def list_services():
    """ Root URL Lists All Services"""
    app.logger.info("Root URL Lists All Services")
    return (
        jsonify(
            name="API_list",
            services=(  ["create customer"],
                        ["add customer"],
                        ["read customer"],
                        ["list customers"],
                        ["update customer"],
                        ["delete customer"],),
            versions=1.0,
            usages=(["Uses username, password, firstname, lastname, and addresses to create an new user and returns the result."],
                    ["Uses username, password, firstname, lastname, and addresses to add an new user into database and returns the result."],
                    ["Finds the customer using a valid customer_id and returns customer's information."],
                    ["Updates customer' information and returns the result."],
                    ["Deletes a customer and all of its information and returns the result."],
                    )
        ),
        status.HTTP_200_OK,
    )
    
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

    customer.create()
    message = customer.serialize()
    location_url = url_for("create_customers", customer_id=customer.id, _external=True)
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
