"""
Customer API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import json
import logging
from unittest import TestCase
from urllib.parse import quote_plus
from werkzeug.exceptions import NotFound
from unittest.mock import MagicMock, patch
from service import status  # HTTP Status Codes
from service.models import db, Customer, Address
from service.routes import app
from tests.factories import CustomerFactory, AddressFactory
from random import randrange

# Disable all but ciritcal errors during normal test run
# uncomment for debugging failing tests
logging.disable(logging.CRITICAL)

BASE_API = "/api/customers"
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap['user-provided'][0]['credentials']['url']
CONTENT_TYPE_JSON="application/json"

######################################################################
#  T E S T   C A S E S
######################################################################

class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Customer.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    def _create_customers(self, count, always_has_address = False):
        """Factory method to create customers in bulk"""
        customers = []
        for _ in range(count):
            test_customer = CustomerFactory()
            test_customer.id = None
            low = 0 if not always_has_address else 1
            for _ in range(randrange(low, 5)):
                test_address = AddressFactory()
                test_customer.addresses.append(test_address)
            resp = self.app.post(
                BASE_API, 
                json = test_customer.serialize(), 
                content_type = CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test customer"
            )
            new_customer = resp.get_json()
            test_customer.id = new_customer["id"]
            for address in test_customer.addresses:
                address.customer_id = new_customer["id"]
            customers.append(test_customer)
        return customers

    def test_create_customer(self):
        """Create a new customer"""
        test_customer = CustomerFactory()
        logging.debug(test_customer)
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_customer = resp.get_json()
        self.assertEqual(new_customer["username"], test_customer.username, "Username do not match")
        self.assertEqual(
            new_customer["password"], test_customer.password, "Password do not match"
        )
        self.assertEqual(
            new_customer["first_name"], test_customer.first_name, "Firstname does not match"
        )
        self.assertEqual(
            new_customer["last_name"], test_customer.last_name, "Lastname does not match"
        )
        self.assertEqual(
            new_customer["addresses"], test_customer.addresses, "Addresses do not match"
        )        
        # try to add the same user with the same username again
        # it should not change the number of customers in the database
        # (beacause username should be unique)
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_create_customer_invalid_value(self):
        """ Create a new customer with a request containing an incorrect value that should have type string """
        test_customer = CustomerFactory()
        test_customer.username = 40
        logging.debug(test_customer)
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_data(self):
         """ Create a Customer with missing data """
         resp = self.app.post(BASE_API, json={}, content_type=CONTENT_TYPE_JSON)
         self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_content_type(self):
         """ Create a Customer with no content type """
         resp = self.app.post(BASE_API)
         self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_address(self):
        """ Create a new address for a customer """
        test_customer = CustomerFactory()
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        customer_id = resp.get_json()["id"]
        test_address = AddressFactory()
        resp = self.app.post(
            "{}/{}/addresses".format(BASE_API, customer_id), json=test_address.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_address = resp.get_json()
        self.assertEqual(
            new_address["customer_id"], customer_id, "Customer id is incorrect"
        )
        self.assertEqual(
            new_address["street_address"], test_address.street_address, 
            "Street address does not match"
        )
        self.assertEqual(
            new_address["city"], test_address.city, "City does not match"
        )
        self.assertEqual(
            new_address["state"], test_address.state, "State does not match"
        )
        self.assertEqual(
            new_address["country"], test_address.country, "Country does not match"
        ) 
        self.assertEqual(
            new_address["zipcode"], test_address.zipcode, "Zipcode does not match"
        )          

    def test_create_customer_address_invalid_value(self):
        """ Create a new address for a customer with a request containing an incorrect value that should have type string """
        test_customer = CustomerFactory()
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        customer_id = resp.get_json()["id"]
        test_address = AddressFactory()
        test_address.street_address = 40
        resp = self.app.post(
            "{}/{}/addresses".format(BASE_API, customer_id), json=test_address.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_address_invalid_zip(self):
        """ Create a new address for a customer with a request containing an incorrect value that should have type int """
        test_customer = CustomerFactory()
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        customer_id = resp.get_json()["id"]
        test_address = AddressFactory()
        test_address.zipcode = 11111
        resp = self.app.post(
            "{}/{}/addresses".format(BASE_API, customer_id), json=test_address.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_customer_not_found(self):
        """ Create a new address for a customer that is not found """
        test_address = AddressFactory()
        resp = self.app.post(
            "{0}/{1}/addresses".format(BASE_API, 1), json=test_address.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        """ Make a call to /api/customers with an unsupported method, PUT """
        resp=self.app.put(BASE_API)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_customer(self):
        """ Get a single Customer """
        # get the id of a customer
        test_customer = self._create_customers(1)[0]
        resp = self.app.get(
            "{0}/{1}".format(BASE_API, test_customer.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["username"], test_customer.username)
        self.assertEqual(data["id"], test_customer.id)
        
    def test_get_customer_not_found(self):
        """ Get a customer thats not found """
        resp = self.app.get("{}/0".format(BASE_API))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_customer_address(self):
        """ Get a single Address for a Customer """
        test_customer = self._create_customers(1, always_has_address = True)[0]
        resp = self.app.get(
            "{0}/{1}".format(BASE_API, test_customer.id), content_type="application/json"
        )
        test_address = resp.get_json()["addresses"][0]
        resp = self.app.get(
            "{}/{}/addresses/{}".format(BASE_API, test_customer.id, test_address["address_id"]),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["street_address"], test_address["street_address"])
        self.assertEqual(data["customer_id"], test_customer.id)
        self.assertEqual(data["address_id"], test_address["address_id"])

    def test_get_address_customer_not_found(self):
        """ Get an address for a customer that's not found """
        resp = self.app.get("{}/1/addresses/1".format(BASE_API))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_address_not_found(self):
        """ Get an address that's not found for an existing customer """
        test_customer = self._create_customers(1, always_has_address = True)[0]
        resp = self.app.get(
            "{0}/{1}".format(BASE_API, test_customer.id), content_type="application/json"
        )
        addresses = resp.get_json()["addresses"]
        address_ids = []
        for address in addresses:
            address_ids.append(address["address_id"])
        query_id = max(address_ids) + 1
        resp = self.app.get("{0}/{1}/addresses/{2}".format(BASE_API, test_customer.id, query_id))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_customer_addresses(self):
        """ Get a single Customer's addresses """
        test_customer = self._create_customers(1)[0]
        resp = self.app.get(
            "{}/{}/addresses".format(BASE_API, test_customer.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        address_ids = set()
        self.assertEqual(len(data), len(test_customer.serialize()["addresses"]))
        for address in test_customer.serialize()["addresses"]:
            address_ids.add(address["street_address"])
        for address in data:
            self.assertTrue(address["street_address"] in address_ids)

    def test_get_customer_addresses_not_found(self):
        """ Get the addresses of a Customer that is not found """
        resp = self.app.get(
            "{}/{}/addresses".format(BASE_API, 0),
            content_type = CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_customer(self):
        """ Test Delete a Customer"""
        test_customer = self._create_customers(1)[0]
        resp = self.app.delete(
            "{0}/{1}".format(BASE_API, test_customer.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{}/{}".format(BASE_API, test_customer.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_address(self):
        """ Test Delete an address from an existing customer"""
        test_customer = self._create_customers(1)[0]
        test_address = AddressFactory()
        test_customer.addresses = [test_address]
        resp = self.app.delete(
            "{0}/{1}/addresses/{2}".format(BASE_API, test_customer.id, 1), content_type="application/json"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

        # make sure it is deleted
        resp = self.app.get(
            "{0}/{1}/addresses/{2}".format(BASE_API, test_customer.id, 1),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # test delete a non-existing address
        resp = self.app.delete(
            "{0}/{1}/addresses/{2}".format(BASE_API, test_customer.id, 1), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

    def test_serve_ui(self):
        """ Test service serves html """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        assert("text/html" in resp.headers['Content-Type'])
        
    def test_update_customer(self):
        """ Update an existing customer """
        # create a customer to update
        test_customer = CustomerFactory()
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the customer
        new_customer = resp.get_json()
        logging.debug(new_customer)
        new_customer["username"] = "new_username"
        resp = self.app.put(
            "{}/{}".format(BASE_API, new_customer["id"]),
            json=new_customer,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_customer = resp.get_json()
        self.assertEqual(updated_customer["username"], "new_username")

    def test_update_customer_missing_data(self):
        """ Update an existing customer using a JSON request body with insufficient data """
        # create a customer to update
        test_customer = CustomerFactory()
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the customer
        new_customer = resp.get_json()
        del new_customer["username"]
        logging.debug(new_customer)

        resp = self.app.put(
            "{}/{}".format(BASE_API, new_customer["id"]),
            json=new_customer,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_not_found(self):
        """ Update a customer that is not found """
        resp = self.app.put(
            "{}/{}".format(BASE_API, 0),
            json={},
            content_type = CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_customer_username_conflict(self):
        """ Update the customer's username to a taken username """
        # create an initial customer
        initial_customer = CustomerFactory()
        resp = self.app.post(
            BASE_API, json=initial_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # create a customer to update
        test_customer = CustomerFactory()
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

         # update the customer
        new_customer = resp.get_json()
        logging.debug(new_customer)
        new_customer["username"] = initial_customer.username
    
        resp = self.app.put(
            "{}/{}".format(BASE_API, new_customer["id"]),
            json=new_customer,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_update_address(self):
        """ Update an existing customer's address """
        # create a customer to update
        test_customer = CustomerFactory()
        test_address = AddressFactory()
        test_customer.addresses = [test_address]
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the customer's addresses
        new_customer = resp.get_json()
        new_address = new_customer["addresses"][0]
        logging.debug(new_address)
        new_address["street_address"] = "^#!"
        resp = self.app.put(
            "{}/{}/addresses/{}".format(BASE_API, new_address["customer_id"], new_address["address_id"]),
            json = new_address,
            content_type = CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_address = resp.get_json()
        self.assertEqual(updated_address, new_address)

    def test_update_addresses_missing(self):
        """ Update an existing customer's address with missing data """
        # create a customer to update
        test_customer = CustomerFactory()
        test_address = AddressFactory()
        test_customer.addresses = [test_address]
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the customer's addresses
        new_customer = resp.get_json()
        new_address = new_customer["addresses"][0]
        logging.debug(new_address)
        del new_address["street_address"]
        resp = self.app.put(
            "{}/{}/addresses/{}".format(BASE_API, new_address["customer_id"], new_address["address_id"]),
            json = new_address,
            content_type = CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_addresses_not_found(self):
        """ Update the address of a customer that is not found """
        resp = self.app.put(
            "{}/{}/addresses/{}".format(BASE_API, 0, 0),
            json={},
            content_type = CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_customer_list(self):
        """Get a list of Customers"""
        self._create_customers(5)
        resp = self.app.get(BASE_API)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_query_customer_list_by_first_name(self):
        """ Query customers by first name """
        customers = self._create_customers(10)
    
        resp = self.app.get(
            "{0}/{1}".format(BASE_API, customers[0].id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_data = resp.get_json()
        new_data["username"] = "!df"
        new_data['last_name'] = 'Johnn'
        #update customer 2 
        self.app.put(
            "{}/2".format(BASE_API),
            json = new_data,
            content_type = CONTENT_TYPE_JSON,
        )
       
        test_first_name = customers[0].first_name
        resp = self.app.get(
            BASE_API, query_string="first_name={}".format(quote_plus(test_first_name))
        )
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()

        resp_all_customer = self.app.get(BASE_API)
        self.assertEqual(resp_all_customer.status_code, status.HTTP_200_OK)
        num_test_customers = [cust for cust in resp_all_customer.get_json() if cust['first_name'] == test_first_name]
     
        self.assertEqual(len(data), len(num_test_customers))
        # check the data just to be sure
        for cust in data:
            self.assertEqual(cust["first_name"], test_first_name)
    
    def test_query_customer_list_by_username(self):
        """ Query customers by username """
        customers = self._create_customers(10)
        
        test_username = customers[0].username
        username_customer = [customer for customer in customers if customer.username == test_username]

        resp = self.app.get(
            BASE_API, query_string="username={}".format(quote_plus(test_username))
        )
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
      
        self.assertEqual(len(data), len(username_customer))
        # check the data just to be sure
        for cust in data:
            self.assertEqual(cust["username"], test_username)
    
    def test_query_customer_list_by_prefix_username(self):
        """ Query customers by prefix of username """
        customers = self._create_customers(10)
        
        test_prefix_username = customers[0].username
        username_customer = [customer for customer in customers if customer.username.startswith(test_prefix_username)]

        resp = self.app.get(
            BASE_API, query_string="prefix_username={}".format(quote_plus(test_prefix_username))
        )
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
      
        self.assertEqual(len(data), len(username_customer))
        # check the data just to be sure
        for cust in data:
            self.assertEqual(cust["username"], test_prefix_username)

    def test_query_customer_list_by_last_name(self):
        """ Query customers by last name """
        customers = self._create_customers(10)
        resp = self.app.get(
            "{0}/{1}".format(BASE_API, customers[0].id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_data = resp.get_json()
        new_data["username"] = "!df"
        new_data['first_name'] = 'Johnn'
        #update customer 1 name
        self.app.put(
            "{}/2".format(BASE_API),
            json = new_data,
            content_type = CONTENT_TYPE_JSON,
        )
        test_last_name = customers[0].last_name
       
        resp = self.app.get(
            BASE_API, query_string="last_name={}".format(quote_plus(test_last_name))
        )
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()

        resp_all_customer = self.app.get(BASE_API)
        self.assertEqual(resp_all_customer.status_code, status.HTTP_200_OK)
        num_test_customers = [cust for cust in resp_all_customer.get_json() if cust['last_name'] == test_last_name]

        self.assertEqual(len(data), len(num_test_customers))
        # check the data just to be sure
        for cust in data:
            self.assertEqual(cust["last_name"], test_last_name)
    
    def test_query_customer_list_by_multiple_query(self):
        """ Query customers by first name and last name """
        customers = self._create_customers(10)
        resp = self.app.get(
            "{0}/{1}".format(BASE_API, customers[0].id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        test_first_name = resp.get_json()['first_name']
        test_last_name = resp.get_json()['last_name']
        new_data = resp.get_json()
        new_data["username"] = "!df"
        new_data['last_name'] = "ddome"
        #update customer 2 last name
        self.app.put(
            "{}/2".format(BASE_API),
            json = new_data,
            content_type = CONTENT_TYPE_JSON,
        )
  
        test_customer = []
        for customer in customers:
          if customer.first_name == test_first_name and customer.last_name == test_last_name:
            test_customer.append(customer)
        dic = {'first_name': quote_plus(test_first_name),
               'last_name': quote_plus(test_last_name)}
        resp = self.app.get(
            BASE_API, 
            query_string= dic
        )
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()

        resp_all_customer = self.app.get(BASE_API)
        self.assertEqual(resp_all_customer.status_code, status.HTTP_200_OK)
        num_test_customers = []
        for cust in resp_all_customer.get_json():
          if cust['last_name'] == test_last_name and cust['first_name'] == test_first_name:
            num_test_customers.append(cust)
       
        self.assertEqual(len(data), len(num_test_customers))
     
        # check the data just to be sure
        for cust in data:
            self.assertEqual(cust["first_name"], test_first_name)
            self.assertEqual(cust["last_name"], test_last_name)

    def test_query_customer_list_by_wrong_query(self):
        """ Query customers by wrong query """
        self._create_customers(10)
        test_age = str(100)
        resp = self.app.get(
            BASE_API, query_string="age={}".format(quote_plus(test_age))
        )
        
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_query_customer_addresses(self):
        """ Query a single Customer's addresses """
        test_customers = self._create_customers(10, always_has_address = True)
        resp = self.app.get(
            "{}/{}".format(BASE_API, test_customers[0].id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        # update the customer's addresses
        new_customer = resp.get_json()
        new_address = new_customer["addresses"][0]
        logging.debug(new_address)
        new_address["country"] = "Dome_country"
        new_address["city"] = "Dome_city"
        pick_resp = self.app.get(
            "{}/{}".format(BASE_API, test_customers[1].id), content_type=CONTENT_TYPE_JSON
        )
        pick_customers = pick_resp.get_json()
        address_id = pick_customers['addresses'][0]['address_id']
        self.app.put(
            "{}/2/addresses/{}".format(BASE_API, address_id),
            json = new_address,
            content_type = CONTENT_TYPE_JSON,
        )
        
        test_country = new_address["country"]
        test_city = new_address["city"]

        
        resp = self.app.get(
            f"{BASE_API}/2/addresses", 
            query_string= {'country': quote_plus(test_country),
                            'city': quote_plus(test_city)}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()[0]['city'], test_city)
        self.assertEqual(resp.get_json()[0]['country'], test_country)
    
    def test_wrong_query_customer_addresses(self):
        """ Query a single Customer's addresses using an unsupported query parameter """
        self._create_customers(10)
        test_mailbox = "123"
        resp = self.app.get(
            f"{BASE_API}/1/addresses", 
            query_string= {'mailbox': quote_plus(test_mailbox)}
        )
      
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_lock_customer(self):
        """ Lock an existing customer """
        # create a customer to test lock
        test_customer = CustomerFactory()
        for _ in range(randrange(0, 5)):
            test_address = AddressFactory()
            test_customer.addresses.append(test_address)
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # lock the customer
        new_customer = resp.get_json()
        logging.debug(new_customer)
        resp = self.app.put(
            "{}/{}/lock".format(BASE_API, new_customer["id"]),
            json=new_customer,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_customer = resp.get_json()
        self.assertEqual(updated_customer["locked"], True)

    def test_lock_customer_not_found(self):
        """ Lock a customer that is not found """
        resp = self.app.put(
            "{}/{}/lock".format(BASE_API, 0),
            json={},
            content_type = CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_unlock_customer(self):
        """ Unlock an existing customer """
        # create a record and lock it
        test_customer = CustomerFactory()
        test_customer.locked=True
        for _ in range(randrange(0, 5)):
            test_address = AddressFactory()
            test_customer.addresses.append(test_address)
        resp = self.app.post(
            BASE_API, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(test_customer.locked, True)

        # unlock the customer
        new_customer = resp.get_json()
        logging.debug(new_customer)
        resp = self.app.put(
            "{}/{}/unlock".format(BASE_API, new_customer["id"]),
            json=new_customer,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_customer = resp.get_json()
        self.assertEqual(updated_customer["locked"], False)

    def test_unlock_customer_not_found(self):
        """ Unlock a customer that is not found """
        resp = self.app.put(
            "{}/{}/unlock".format(BASE_API, 0),
            json={},
            content_type = CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)