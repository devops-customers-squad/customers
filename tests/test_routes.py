"""
Customer API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
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

BASE_URL = "/customers"
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)
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

    def _create_customers(self, count):
        """Factory method to create customers in bulk"""
        customers = []
        for _ in range(count):
            test_customer = CustomerFactory()
            test_customer.id = None
            for _ in range(randrange(0, 5)):
                test_address = AddressFactory()
                test_customer.addresses.append(test_address)
            resp = self.app.post(
                BASE_URL, 
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
            BASE_URL, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
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
            new_customer["addresses"], test_customer.addresses, "Firstname does not match"
        )        
        # try to add the same user with the same username again
        # it should not change the number of customers in the database
        # (beacause username should be unique)
        resp = self.app.post(
            BASE_URL, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_create_customer_no_data(self):
         """Create a Customer with missing data"""
         resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
         self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_content_type(self):
         """Create a Customer with no content type"""
         resp = self.app.post(BASE_URL)
         self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
    def test_method_not_allowed(self):
        resp=self.app.put('/customers')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_customer(self):
        """ Get a single Customer """
        # get the id of a customer
        test_customer = self._create_customers(1)[0]
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, test_customer.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["username"], test_customer.username)
        self.assertEqual(data["id"], test_customer.id)
        
    def test_get_customer_not_found(self):
        """ Get a customer thats not found """
        resp = self.app.get("{}/0".format(BASE_URL))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_customer_addresses(self):
        """ Get a single Customer's addresses """
        test_customer = self._create_customers(1)[0]
        resp = self.app.get(
            "{}/{}/addresses".format(BASE_URL, test_customer.id), content_type="application/json"
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
        """ Get the address of a Customer that is not found """
        resp = self.app.get(
            "/customers/{}/addresses".format(0),
            content_type = CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_customer(self):
        """ Test Delete a Customer"""
        test_customer = self._create_customers(1)[0]
        resp = self.app.delete(
            "{0}/{1}".format(BASE_URL, test_customer.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{}/{}".format(BASE_URL, test_customer.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_services_list(self):
        """ Test services list call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "Customers REST API Service")
        
    def test_update_customer(self):
        """ Update an existing customer """
        # create a customer to update
        test_customer = CustomerFactory()
        resp = self.app.post(
            BASE_URL, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the customer
        new_customer = resp.get_json()
        logging.debug(new_customer)
        new_customer["username"] = "new_username"
        resp = self.app.put(
            "/customers/{}".format(new_customer["id"]),
            json=new_customer,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_customer = resp.get_json()
        self.assertEqual(updated_customer["username"], "new_username")

    def test_update_customer_addresses_not_found(self):
        """ Update the addresses of a customer that is not found """
        resp = self.app.put(
            "/customers/{}".format(0),
            json={},
            content_type = CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_customer_username_conflict(self):
        """ Update the customer's username to a taken username """
        # create an initial customer
        initial_customer = CustomerFactory()
        resp = self.app.post(
            BASE_URL, json=initial_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # create a customer to update
        test_customer = CustomerFactory()
        resp = self.app.post(
            BASE_URL, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

         # update the customer
        new_customer = resp.get_json()
        logging.debug(new_customer)
        new_customer["username"] = initial_customer.username
    
        resp = self.app.put(
            "/customers/{}".format(new_customer["id"]),
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
            BASE_URL, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the customer's addresses
        new_customer = resp.get_json()
        new_address = new_customer["addresses"][0]
        logging.debug(new_address)
        new_address["street_address"] = "^#!"
        resp = self.app.put(
            "/customers/{}/addresses/{}".format(new_address["customer_id"], new_address["address_id"], ),
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
            BASE_URL, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the customer's addresses
        new_customer = resp.get_json()
        new_address = new_customer["addresses"][0]
        logging.debug(new_address)
        del new_address["street_address"]
        resp = self.app.put(
            "/customers/{}/addresses/{}".format(new_address["customer_id"], new_address["address_id"], ),
            json = new_address,
            content_type = CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_addresses_not_found(self):
        """ Update the addresses of a customer that is not found """
        resp = self.app.put(
            "/customers/{}/addresses/{}".format(0, 0),
            json={},
            content_type = CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_customer_list(self):
        """Get a list of Customers"""
        self._create_customers(5)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_query_customer_list_by_first_name(self):
        """ Query customers by first name """
        customers = self._create_customers(10)
    
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, customers[0].id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_data = resp.get_json()
        new_data["username"] = "!df"
        new_data['last_name'] = 'Johnn'
        #update customer 2 
        resp = self.app.put(
            "/customers/2",
            json = new_data,
            content_type = CONTENT_TYPE_JSON,
        )
       
        test_first_name = customers[0].first_name
        resp = self.app.get(
            BASE_URL, query_string="first_name={}".format(quote_plus(test_first_name))
        )
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
       
        self.assertEqual(len(data), 2)
        # check the data just to be sure
        for cust in data:
            self.assertEqual(cust["first_name"], test_first_name)
    
    def test_query_customer_list_by_username(self):
        """ Query customers by username """
        customers = self._create_customers(10)
        
        test_username = customers[0].username
        username_customer = [customer for customer in customers if customer.username == test_username]

        resp = self.app.get(
            BASE_URL, query_string="username={}".format(quote_plus(test_username))
        )
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
      
        self.assertEqual(len(data), len(username_customer))
        # check the data just to be sure
        for cust in data:
            self.assertEqual(cust["username"], test_username)
    
    def test_query_customer_list_by_last_name(self):
        """ Query customers by last name """
        customers = self._create_customers(10)
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, customers[0].id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_data = resp.get_json()
        new_data["username"] = "!df"
        new_data['first_name'] = 'Johnn'
        #update customer 1 name
        resp = self.app.put(
            "/customers/2",
            json = new_data,
            content_type = CONTENT_TYPE_JSON,
        )
        test_last_name = customers[0].last_name
       
        resp = self.app.get(
            BASE_URL, query_string="last_name={}".format(quote_plus(test_last_name))
        )
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
      
        self.assertEqual(len(data), 2)
        # check the data just to be sure
        for cust in data:
            self.assertEqual(cust["last_name"], test_last_name)
    
    def tesquery_customer_list_by_multiple_query(self):
        """ Query customers by first name and last name """
        customers = self._create_customers(10)
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, customers[0].id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_data = resp.get_json()
        new_data["username"] = "!df"
        #update customer 1 name
        resp = self.app.put(
            "/customers/2",
            json = new_data,
            content_type = CONTENT_TYPE_JSON,
        )
       
        test_first_name = customers[0].first_name
        test_last_name = customers[1].last_name
 
        test_customer = []
        for customer in customers:
          if customer.first_name == test_first_name and customer.last_name == test_last_name:
            test_customer.append(customer)
        dic = {'first_name': quote_plus(test_first_name),
               'last_name': quote_plus(test_last_name)}
        resp = self.app.get(
            BASE_URL, 
            query_string= dict
        )
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
     
        self.assertEqual(len(data), 2)
        # check the data just to be sure
        for cust in data:
            self.assertEqual(cust["first_name"], test_first_name)
            self.assertEqual(cust["last_name"], test_last_name)

    def test_query_customer_list_by_wrong_query(self):
        """ Query customers by wrong query """
        self._create_customers(10)
        test_age = str(100)
        resp = self.app.get(
            BASE_URL, query_string="age={}".format(quote_plus(test_age))
        )
        
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    
    
