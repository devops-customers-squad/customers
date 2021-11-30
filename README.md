# customers
[![build](https://github.com/devops-customers-squad/customers/actions/workflows/ci.yml/badge.svg)](https://github.com/devops-customers-squad/customers/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/devops-customers-squad/customers/branch/main/graph/badge.svg?token=4E1ONO9584)](https://codecov.io/gh/devops-customers-squad/customers)

This repository contains the implementation of the customers RESTful Flask service to be used by the eCommerce site.

## Running the service
To install the requirements for the service, from the command line run:
```bash
    pip install -r requirements.txt
```

To start the service, from the command line run:
```bash
    FLASK_APP=service:app flask run -h 0.0.0.0
```

The app runs on `localhost:5000`

## Testing the service 
To run the tests for the service, from the command line run:
```bash
    nosetests
```

## Available endpoints
- Access basic useful information about the API
    * `GET /customers/`

- Create a customer: 
    * `POST /customers`
    * The JSON request body for creating a customer is expected to contain the following keys: ``first_name, last_name, user_name, password，addresses, street_address, state, city, and zipcode``
    * The expected types of the values for each of the expected keys are as follows:
        - first_name: string
        - last_name: string
        - user_name: string
        - password: string 
        - addresses: array of JSON objects, each of which contains:
            - street_address: string
            - state: string
            - city: string
            - zipcode: integer
            - country: string
       
        
    * Sample JSON request body format:
    ```
    {
        "first_name": "John",
        "last_name": "Smith",
        "username": "xxx",
        "password": "XXX",
        "addresses": [{
            "street_address" : "123 Fake Road",
            "city" : "New York",
            "state" : "NY",
            "zipcode" : 10001,
            "country" : "USA"
        }] 
    }
    ```
- Read a customer's information:
    * `GET /customers/{customer_id}`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
- Update a customer's information:
    * `PUT /customers/{customer_id}`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
    * The JSON request body is expected to contain all of the following keys: ``first_name, last_name, user_name, password``
    * If the JSON request body is missing one or more of the required keys, an error will be thrown
    * The expected types of the values for each of the possible keys are as follows:
        - first_name: string
        - last_name: string
        - user_name: string
        - password: string 
    * Sample JSON request body format:
    ```
    { 
        "first_name": "John",  
        "last_name": "Smith",  
        "username": "XXX", 
        "password": "XXX" 
    }
    ```
- Update a customer's address:
    * `PUT /customers/{customer_id}/addresses/{address_id}`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer and the parameter address_id is expect3ed to be equal to the unique id of an address belonging to the specified customer
    * The JSON request body is expected to contain the keys ``street_address, city, state, zipcode, and country``. All keys except for zipcode expect a string; zipcode expects an integer
    * Sample JSON request body format:
    ```
    {
         "street_address" : "123 Fake Road",
         "city" : "New York",
         "state" : "NY",
         "zipcode" : 10001,
         "country" : "USA"
    }
    ```
    * If successful, the address with address_id belonging to the customer with customer_id will be equivalent to the address represented in the JSON request body

- Delete a customer
    * `DELETE /customers/{customer_id}`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
- List the information for all registered customers:
    * `GET /customers` 
- Query customers by first name and/or last name
    * `GET /customer?first_name={first name}`
    * The parameter the first name is expected to be a string equal to the unique first name of a customer
    * `GET /customer?last_name={last name}`
    * The parameter the last name is expected to be a string equal to the unique last name of a customer
    * Additionally, it is possible to query by first_name and last_name together: `GET /customer?last_name={last name}&first_name={first name}`
- Query customers by the prefix of their usernames
    * `GET/customer?prefix_username={the prefix of username}`
    * The parameter the prefix of username is expected to be a string equal to the unique prefix of a customer's username
- Mark customers' accounts as locked
    * `PUT /customers/{customer_id}/lock`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
    
- Mark customers' accounts as unlocked
    * `PUT /customers/{customer_id}/unlock`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer

- List customers'addresses
    * `GET /customers/{customer_id}/addresses`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
 
- List customers'addresses that match a specific query
    * `GET /customers/{customer_id}/addresses?{query string}`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
    * The endpoint requires a valid customer_id and accepted keys in the query string will include street_address, state, city, country, and zipcode
    
