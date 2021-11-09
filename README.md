# customers
[![Build Status](https://app.travis-ci.com/devops-customers-squad/customers.svg?branch=main)](https://app.travis-ci.com/devops-customers-squad/customers)
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

- Create a customer: 
    * `POST /customers`
    * The JSON request body for creating a customer is expected to contain the following keys: ``first_name, last_name, user_name, addresses, password``
    * The expected types of the values for each of the expected keys are as follows:
        - first_name: string
        - last_name: string
        - user_name: string
        - addresses: array of string
        - password: string 
    * Sample JSON request body format:
    ```
    {
        "first_name": "John",  
        "last_name": "Smith",  
        "username": "XXX",  
        "addresses": ["123 Main St, Buffalo, NY", "50 John Street, NY"],  
        "password": "XXX"  
    }
    ```
- Read a customer's information:
    * `GET /customers/{customer_id}`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
- List the information for all registered customers:
    * `GET /customers`
- Update a customer's information:
    * `PUT /customers/{customer_id}`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
    * The JSON request body is expected to contain all of the following keys: ``first_name, last_name, user_name, addresses, password``
    * If the JSON request body is missing one or more of the required keys, an error will be thrown
    * The expected types of the values for each of the possible keys are as follows:
        - first_name: string
        - last_name: string
        - user_name: string
        - addresses: array of strings
        - password: string 
    * Sample JSON request body format:
    ```
    { 
        "first_name": "Johnny", 
        "password": "YYY"
    }
    ```
- Update a customer's addresses:
    * `PUT /customers/{customer_id}/addresses`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
    * The JSON request body is expected to contain the key ``addresses`` and the value of the key is expected to be an array of strings
    * Sample JSON request body format:
    ```
    { 
        "addresses": ["123 Main St, Buffalo, NY", "50 John Street, NY"]  
    }
    ```
    * If successful, the stored addresses of the customer will be equivalent to the value of the ``addresses`` key in the JSON request body
- Delete a customer
    * `DELETE /customers/{customer_id}`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
- Access basic useful information about the API
    * `GET /customers/`
- Query customers by first name/last name
    * `GET /customer?first_name={first name}`
    * The parameter the first name is expected to be a string equal to the unique first name of a customer
    * `GET /customer?last_name={last name}`
    * The parameter the last name is expected to be a string equal to the unique last name of a customer
- Query customers by the prefix of their usernames
    * `GET/customer?prefix_username={the prefix of username}`
    * The parameter the prefix of username is expected to be a string equal to the unique prefix of a customer's username
- Mark customers' accounts as locked
    * `PUT /customers/{customer_id}/lock`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
    * The JSON request body is expected to contain all of the following keys: ``locked``
    * Sample JSON request body format:
    ```
    { 
        locked: true  
    }
    ```
- Mark customers' accounts as unlocked
 * `PUT /customers/{customer_id}/unlock`
 * The parameter customer_id is expected to be an integer equal to the unique id of a customer
 * The JSON request body is expected to contain all of the following keys: ``locked``    
 * Sample JSON request body format:
    ```
    { 
        locked: false  
    }
    ```
- List customers'addresses that match a specific query
* `GET /customers/{customer_id}/addresses?{query string}`
* The parameter customer_id is expected to be an integer equal to the unique id of a customer
* The JSON request body is expected to contain all of the following keys: ``state, city, zip, and country``
* Sample JSON request body format:
    ```
    { 
      "state": "NY",
      "city": "New York",
      "zip": 10001,
      "country": "USA"  
    }
    ```

