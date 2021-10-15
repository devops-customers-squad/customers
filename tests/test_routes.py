"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
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
                resp.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_customer = resp.get_json()
            test_customer.id = new_customer["id"]
            customers.append(test_customer)
        return customers

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

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
        # Check that the location header was correct
        # WE DO NOT HAVE A GET METHOD YET
        #resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        #self.assertEqual(resp.status_code, status.HTTP_200_OK)
        #new_customer = resp.get_json()
        #self.assertEqual(new_customer["name"], test_customer.name, "Names do not match")
        #self.assertEqual(
        #    new_customer["category"], test_customer.category, "Categories do not match"
        #)
        #self.assertEqual(
        #    new_customer["available"], test_customer.available, "Availability does not match"
        #)

    def test_create_customer_no_data(self):
         """Create a Product with missing data"""
         resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
         self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_content_type(self):
         """Create a Product with no content type"""
         resp = self.app.post(BASE_URL)
         self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
    def test_method_not_allowed(self):
        resp=self.app.get('/customers')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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
