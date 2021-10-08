# customers
This repository contains the implementation of the customers RESTful Flask service to be used by the eCommerce site.

## Running the service
To install the requirements for the service, from the command line run:
```bash
    pip install -r requirements.txt
```

To start the service, from the command line run:
```bash
    FLASK_APP=service:app flask run
```

The app runs on `localhost:5000`

## Testing the service 
To run the tests for the service (with color, if supported by your command shell), from the command line run:
```bash
    nosetests --with-spec --spec-color
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
        first_name: "John",  
        last_name: "Smith",  
        user_name: "XXX",  
        addresses: ["123 Main St, Buffalo, NY", "50 John Street, NY"],  
        password: "XXX"  
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
    * The JSON request body is expected to contain one or more of the following keys: ``first_name, last_name, user_name, addresses, password``
    * The expected types of the values for each of the possible keys are as follows:
        - first_name: string
        - last_name: string
        - user_name: string
        - addresses: array of strings
        - password: string 
    * Sample JSON request body format:
    ```
    { 
        first_name: "Johnny", 
        password: "YYY"
    }
    ```
- Update a customer's addresses:
    * `PUT /customers/{customer_id}/addresses`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
    * The JSON request body is expected to contain the key ``addresses`` and the value of the key is expected to be an array of strings
    * Sample JSON request body format:
    ```
    { 
        addresses: ["123 Main St, Buffalo, NY", "50 John Street, NY"]  
    }
    ```
    * If successful, the stored addresses of the customer will be equivalent to the value of the ``addresses`` key in the JSON request body
- Delete a customer
    * `DELETE /customers/{customer_id}`
    * The parameter customer_id is expected to be an integer equal to the unique id of a customer
- Access basic useful information about the API
    * `GET /customers/`
