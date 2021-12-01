"""
Customer Service

A service for manipulating and accessing customer information for the eCommerce site
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, make_response, abort
from flask_restx import Api, Resource, fields, reqparse, inputs
from . import status  # HTTP Status Codes

from flask_sqlalchemy import SQLAlchemy
from service.models import Customer, Address, DataValidationError, ResourceConflictError, UnsupportedKeyError
from werkzeug.exceptions import NotFound
# Import Flask application
from . import app

######################################################################
# Serve UI HTML 
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file("index.html")

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Customers REST API Service',
          description='This is the Fall 2021 NYU DevOps Customers service.',
          default='customers',
          default_label='Customers operations',
          doc='/apidocs/',
          prefix='/api'
         )

create_address_model = api.model('Address', {
    'street_address': fields.String(required=True,
                                description='The street address for the customer\'s address'),
    'city': fields.String(required=True,
                                description='The city for the customer\'s address'),
    'state': fields.String(required=True,
                                description='The state for the customer\'s address'),
    'zipcode': fields.Integer(required=True,
                                description='The zipcode for the customer\'s address'),                        
    'country': fields.String(required=True,
                                description='The country for the customer\'s address')   
})

address_model = api.inherit(
    'AddressModel', 
    create_address_model,
    {
        'customer_id': fields.Integer(readOnly=True,
                                description='The unique id for the customer that the address belongs to'),
        'address_id': fields.Integer(readOnly=True,
                                description='The unique id for the customer\'s address')                            
    }    
)

update_customer_model = api.model('Customer', {
    'first_name': fields.String(required=True,
                                description='The first name for the customer'),
    'last_name': fields.String(required=True,
                                description='The last name for the customer'),    
    'username': fields.String(required=True,
                                description='The username of the customer'),
    'password': fields.String(required=True,
                                description='The password for the customer')
})

create_customer_model = api.inherit(
    'CustomerWithAddress', 
    update_customer_model,
    {
        'addresses': fields.List(fields.Nested(address_model),
                                required=True,
                                description='The addresses belonging to the customer')                       
    }    
)

customer_model = api.inherit(
    "CustomerModel",
    create_customer_model,
    {
        'id': fields.Integer(readOnly=True,
                                    description='The unique id for the customer'),
        'locked': fields.Boolean(readOnly=True,
                                    description='Is the customer\'s account locked?')
    }
)

customer_args = reqparse.RequestParser()
customer_args.add_argument('username', type=str, required=False, help='List Customers by username')
customer_args.add_argument('first_name', type=str, required=False, help='List Customers by first name')
customer_args.add_argument('last_name', type=str, required=False, help='List Customers by last name')
customer_args.add_argument('prefix_username', type=str, required=False, help='List Customers by username prefix')

address_args = reqparse.RequestParser()
address_args.add_argument('street_address', type=str, required=False, help='List Customer\'s Addresses by street address')
address_args.add_argument('city', type=str, required=False, help='List Customer\'s Addresses by city')
address_args.add_argument('state', type=str, required=False, help='List Customer\'s Addresses by state')
address_args.add_argument('zipcode', type=int, required=False, help='List Customer\'s Addresses by zipcode')
address_args.add_argument('country', type=str, required=False, help='List Customer\'s Addresses by country')

######################################################################
# Special Error Handlers
###################################################################### 
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """Handles Value Errors from bad data"""
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST

@api.errorhandler(ResourceConflictError)
def request_conflict_error(error):
    """Handles errors from conflicts with existing resources"""
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_409_CONFLICT,
        'error': 'Conflict',
        'message': message
    }, status.HTTP_409_CONFLICT

@api.errorhandler(UnsupportedKeyError)
def request_unsupported_key(error):
    """Handles errors from invalid query parameters"""
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Unsupported Key',
        'message': message
    }, status.HTTP_400_BAD_REQUEST

######################################################################
# PATH: /customers/{customer_id}/addresses/{address_id}
######################################################################
@api.route('/customers/<int:customer_id>/addresses/<int:address_id>')
@api.param('customer_id', 'The Customer identifier')
@api.param('address_id', 'The Address identifier')
class AddressResource(Resource):
    """
    AddressResource class

    Allows the manipulation and accessing of a single Customer's Address
    
    GET /customers/{customer_id}/addresses/{address_id} - Returns the address
        with id address_id belonging to the customer with id customer_id
    PUT /customers/{customer_id}/addresses/{address_id} - Updates the address
        with id address_id belonging to the customer with id customer_id
    DELETE /customers/{customer_id}/addresses/{address_id} -  Deletes the address
        with id address_id belonging to the customer with id customer_id
    """
    #------------------------------------------------------------------
    # RETRIEVE A CUSTOMER'S ADDRESS
    #------------------------------------------------------------------
    @api.doc('get_addresses')
    @api.response(404, 'The specified address belonging to the specified customer was not found')
    @api.marshal_with(address_model)
    def get(self, customer_id, address_id):
        """
        Retrieve a single customer's address
        This endpoint will return an address for a customer based on the 
        customer's and address' ids
        """
        app.logger.info(f"Request address with address_id {address_id} for customer with customer_id {customer_id}")
    
        address = Address.find(address_id)
        if not address or address.customer_id != customer_id:
            raise NotFound("Address with id '{}' for customer with id '{}' was not found.".format(address_id, customer_id))
        return address.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE A CUSTOMER'S ADDRESS
    #------------------------------------------------------------------
    @api.doc('update_addresses')
    @api.response(404, 'The specified address belonging to the specified customer was not found')
    @api.response(400, 'The supplied Address data was not valid')
    @api.expect(create_address_model)
    @api.marshal_with(address_model)   
    def put(self, customer_id, address_id):
        """
        Update a Customer's address
        This endpoint will update a Customer's addresses based on the request body.
        """
        app.logger.info("Request to update addresses of Customer with id: %s", customer_id)
        check_content_type("application/json")
        check_address_data(api.payload)
        address = Address.find(address_id)
        if not address or address.customer_id != customer_id:
            raise NotFound("Address with id '{}' for customer with id '{}' was not found.".format(address_id, customer_id))

        address.deserialize(api.payload)
        address.address_id = address_id
        address.update()

        app.logger.info("address with ID [%s] for customer with ID [%s] updated.", address.address_id, customer_id)
        return address.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A CUSTOMER'S ADDRESS
    #------------------------------------------------------------------
    @api.doc('delete_addresses')
    @api.response(204, 'Address deleted')
    def delete(self, customer_id, address_id):
        """
        Delete an existing customer's address
        This endpoint will delete a Customer's address based the customer_id and address_id specified in the path.
        """
        app.logger.info("Request to delete address with id: %s, customer with id: %s", address_id, customer_id)
        customer = Customer.find(customer_id)
        if customer:
            address = Address.find(address_id)
            if address: address.delete()
        return "", status.HTTP_204_NO_CONTENT

######################################################################
# PATH: /customers/{customer_id}/addresses
######################################################################
@api.route('/customers/<int:customer_id>/addresses')
@api.param('customer_id', 'The Customer identifier')
class AddressCollection(Resource):
    """
    AddressCollections class

    Allows the manipulation and accessing of a Customer's Addresses
    
    GET /customers/{customer_id}/addresses - Returns the addresses
        belonging to the customer with id customer_id
    POST /customers/{customer_id}/addresses - Creates a new address for
        the customer with id customer_id
    """
    #------------------------------------------------------------------
    # CREATE A NEW ADDRESS FOR THE CUSTOMER
    #------------------------------------------------------------------
    def post(self, customer_id):
        """
        Creates an Address for the Customer with an id equal to customer_id
        This endpoint will create an Address for the Customer with an id equal
        to the customer_id based on the data in the request body
        """  
        app.logger.info("Request to create address for customer with id {}".format(customer_id))
        check_content_type("application/json")
        check_address_data(api.payload)
        customer = Customer.find(customer_id)
        if not customer:
            raise NotFound(f"Customer with id '{customer_id}' was not found.")
        address = Address()
        address.deserialize(api.payload)
        address.customer_id = customer_id
        address.create()
        message = address.serialize()
        location_url = api.url_for(AddressResource, customer_id = customer.id, 
            address_id = address.address_id, _external = True)
        return message, status.HTTP_201_CREATED, {"Location": location_url}

    #------------------------------------------------------------------
    # RETRIEVE A CUSTOMER'S ADDRESSES
    #------------------------------------------------------------------
    def get(self, customer_id):
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
                    raise UnsupportedKeyError("The query key: '" + key + "' is not supported.")

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

        return addresses, status.HTTP_200_OK

######################################################################
# PATH: /customers/{customer_id}/lock
######################################################################
@api.route('/customers/<int:customer_id>/lock')
@api.param('customer_id', 'The Customer identifier')
class LockAction(Resource):
    """
    LockAction class

    Allows for the manipulation of Customers to mark their accounts as locked
    
    PUT /customers/{customer_id}/lock - Sets the locked attribute of the
        customer with id customer_id to true
    """
    #------------------------------------------------------------------
    # LOCK AN EXISTING CUSTOMER
    #------------------------------------------------------------------
    def put(self, customer_id):
        """
        Lock a Customer
        """
        app.logger.info("Request to lock Customer with id: %s", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            raise NotFound("customer with id '{}' was not found.".format(customer_id))
        customer.locked = True
        customer.update()
        app.logger.info("customer with ID [%s] is locked.", customer.id)
        return customer.serialize_for_lock(), status.HTTP_200_OK

######################################################################
# PATH: /customers/{customer_id}/unlock
######################################################################
@api.route('/customers/<int:customer_id>/unlock')
@api.param('customer_id', 'The Customer identifier')
class UnlockAction(Resource):
    """
    UnlockAction class

    Allows for the manipulation of Customers to mark their accounts as not locked
    
    PUT /customers/{customer_id}/unlock - Sets the locked attribute of the
        customer with id customer_id to false
    """
    #------------------------------------------------------------------
    # UNLOCK AN EXISTING CUSTOMER
    #------------------------------------------------------------------
    def put(self, customer_id):
        """
        Unock a Customer
        """
        app.logger.info("Request to lock Customer with id: %s", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            raise NotFound("customer with id '{}' was not found.".format(customer_id))
        customer.locked = False
        customer.update()
        app.logger.info("customer with ID [%s] is unlocked.", customer.id)
        return customer.serialize_for_lock(), status.HTTP_200_OK

######################################################################
# PATH: /customers/{customer_id}
######################################################################
@api.route('/customers/<int:customer_id>')
@api.param('customer_id', 'The Customer identifier')
class CustomerResource(Resource):
    """
    CustomerResource class

    Allows the manipulation and accessing of a single Customer
    
    GET /customers/{customer_id} - Returns the customer with id customer_id
    PUT /customers/{customer_id} - Updates the customer with id customer_id
    DELETE /customers/{customer_id} -  Deletes the customer with id customer_id
    """
    #------------------------------------------------------------------
    # RETRIEVE AN EXISTING CUSTOMER
    #------------------------------------------------------------------
    @api.doc('get_customers')
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def get(self, customer_id):
        """
        Retrieve a single customer
        This endpoint will return a customer based on their id
        """
        app.logger.info("Request information for customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            raise NotFound("Customer with id '{}' was not found.".format(customer_id))
        return customer.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING CUSTOMER
    #------------------------------------------------------------------
    @api.doc('update_customers')
    @api.response(404, 'Customer not found')
    @api.response(400, 'The posted Customer data was not valid')
    @api.expect(customer_model)
    @api.marshal_with(customer_model)
    def put(self, customer_id):
        """
        Update a Customer
        This endpoint will update a Customer based the body that is posted
        """
        app.logger.info("Request to update Customer with id: [%s]", customer_id)
        check_content_type("application/json")
        check_customer_data(api.payload)
        request_data = api.payload
        customer = Customer.find(customer_id)
        if not customer:
            raise NotFound("customer with id '{}' was not found.".format(customer_id))
        
        try:
            if "username" in request_data:
                other_customer = Customer.find_by_name(request_data["username"]).first()
                if other_customer is not None and other_customer.id != customer_id:
                    raise ResourceConflictError("Username '" + request_data["username"] + "' already exists.")
            customer.username = request_data["username"]
            customer.id = customer_id
            customer.first_name = request_data["first_name"]
            customer.last_name = request_data["last_name"]
            customer.password = request_data["password"]
            customer.update()
        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer update: missing " + error.args[0]
            )
        app.logger.info("customer with ID [%s] updated.", customer.id)
        return customer.serialize(), status.HTTP_200_OK
    
    #------------------------------------------------------------------
    # DELETE A CUSTOMER
    #------------------------------------------------------------------
    @api.doc('delete_customers')
    @api.response(204, 'Customer deleted')
    def delete(self, customer_id):
        """
        Delete a Customer
        This endpoint will delete a Customer based the id specified in the path
        """
        app.logger.info("Request to delete customer with id: %s", customer_id)
        customer = Customer.find(customer_id)
        if customer:
            customer.delete()
        return "", status.HTTP_204_NO_CONTENT
    
######################################################################
# PATH: /customers
######################################################################
@api.route('/customers')
class CustomerCollection(Resource):
    """
    CustomerCollections class

    Allows the manipulation and accessing of a Customer
    
    GET /customers - Returns the information for all stored Customers
    POST /customers - Creates a new Customer
    """
    #------------------------------------------------------------------
    # CREATE A NEW CUSTOMER
    #------------------------------------------------------------------
    def post(self):
        """
        Creates a Customer
        This endpoint will create a Customer based the data in the body that is posted
        """
        app.logger.info("Request to create a customer")
        check_content_type("application/json")
        check_customer_data(api.payload)
        check_addresses_data(api.payload)
        customer = Customer()
        customer.deserialize(api.payload)
        customer_found = Customer.find_by_name(customer.username).first()
        if customer_found:
            raise ResourceConflictError( "Username '" + customer.username + "' already exists.")
        customer.locked=False
        customer.create()
        message = customer.serialize()
        location_url = api.url_for(CustomerResource, customer_id=customer.id, _external=True)
        return message, status.HTTP_201_CREATED, {"Location": location_url}

    #------------------------------------------------------------------
    # LIST ALL CUSTOMERS
    #------------------------------------------------------------------
    def get(self):
        """Returns all of the customers"""
        app.logger.info("Request for customer list")
        
        all_query_key = ["username", "first_name", "last_name", "prefix_username"]
        for key in request.args.keys():
            if key not in all_query_key:
                raise UnsupportedKeyError("The query key: '" + key + "' is not supported.")
        
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
        return results, status.HTTP_200_OK

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

def check_customer_data(request):
    string_keys = ["first_name", "last_name", "username", "password"]
    for key in string_keys:
        if key in request and not isinstance(request[key], str):
            app.logger.error("Invalid customer request value for key '%s'", key)
            abort(status.HTTP_400_BAD_REQUEST, "Request body must have a value of type string for the key '{}'".format(key))

def check_address_data(request):
    string_keys = ["street_address", "city", "state", "country"]
    int_keys = ["zipcode"]
    for key in string_keys:
        if key in request and not isinstance(request[key], str):
            app.logger.error("Invalid address request value for key '%s'", key)
            abort(status.HTTP_400_BAD_REQUEST, "Request body must have a value of type string for the key '{}'".format(key))
    for key in int_keys:
        if key in request and not isinstance(request[key], int):
            app.logger.error("Invalid address request value for key '%s'", key)
            abort(status.HTTP_400_BAD_REQUEST, "Request body must have a value of type int for the key '{}'".format(key))        

def check_addresses_data(request):
    if "addresses" in request:
        addresses = request["addresses"]
        for address in addresses:
            check_address_data(address)