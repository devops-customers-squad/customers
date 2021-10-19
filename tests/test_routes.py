"""
Customer API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

from werkzeug.exceptions import NotFound
from service import status  # HTTP Status Codes
from service.models import db, Customer
from service.routes import app
from tests.factories import CustomerFactory

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
            customers.append(test_customer)
        return customers

    #def test_create_a_customer(self):
    #    """ Create a customer and assert that it exists """
    #    customer = Customer(username="LYCC", password="123", first_name="Yongchang", last_name="Liu",addresses=[["WWH"]])
    #    self.assertTrue(customer != None)
    #    self.assertEqual(customer.id, None)
    #    self.assertEqual(customer.username, "Liu")
    #    self.assertEqual(customer.password, "123")
    #    self.assertEqual(customer.first_name, "Yongchang")
    #    self.assertEqual(customer.last_name, "Liu")
    #    self.assertEqual(customer.addresses, ["WWH"])

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

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_customer_list(self):
        """Get a list of Customers"""
        self._create_customers(5)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

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

    #def test_services_list(self):
       # """ Test services list call """
      #  resp = self.app.get("/customers")
      #  self.assertEqual(resp.status_code, status.HTTP_200_OK)
     #   data = resp.get_json()
     #   self.assertEqual(data["name"], "API_list")


    def test_services_list(self):
        """ Test services list call """
        resp = self.app.get("/services")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], "API_list")
        
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


    def test_update_customer_not_found(self):
        """ Update the addresses of a customer that is not found """
        resp = self.app.put(
            "/customers/{}".format(0),
            content_type = CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_addresses(self):
        """ Update an existing customer's addresses """
        # create a customer to update
        test_customer = CustomerFactory()
        resp = self.app.post(
            BASE_URL, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the customer's addresses
        new_address_customer = resp.get_json()
        logging.debug(new_address_customer)
        new_addresses = ["123 testing lane", "932 my new address"]
        new_address_customer["addresses"] = new_addresses
        resp = self.app.put(
            "/customers/{}/addresses".format(new_address_customer["id"]),
            json = new_address_customer,
            content_type = CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_customer = resp.get_json()
        self.assertEqual(updated_customer["addresses"], new_addresses)

    def test_update_addresses_missing(self):
        """ Update a customer's addresses with addresses missing in request """
        # create a customer to update
        test_customer = CustomerFactory()
        resp = self.app.post(
            BASE_URL, json=test_customer.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the customer's addresses
        new_address_customer = resp.get_json()
        logging.debug(new_address_customer)
        resp = self.app.put(
            "/customers/{}/addresses".format(new_address_customer["id"]),
            json = dict(),
            content_type = CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_addresses_not_found(self):
        """ Update the addresses of a customer that is not found """
        resp = self.app.put(
            "/customers/{}/addresses".format(0),
            content_type = CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    
   # def test_update_customer_not_found(self):
    #    """Update an non-existing customer"""
      
        # update the customer
     #   new_customer = CustomerFactory().serialize()
    #    logging.debug(new_customer)
        
     #   resp = self.app.put(
     #       "/customers/10",
     #       json=new_customer,
     #       content_type=CONTENT_TYPE_JSON,
     #   )
      
      #  self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
       
    
    

