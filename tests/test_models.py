"""
Test cases for Customer Model

"""
import logging
import unittest
import os
from service import app
from service.models import Customer, DataValidationError, db
from werkzeug.exceptions import NotFound
from tests.factories import CustomerFactory

BASE_URL = "/customers"
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)
CONTENT_TYPE_JSON="application/json"

######################################################################
#  CUSTOMER   M O D E L   T E S T   C A S E S
######################################################################
class TestYourResourceModel(unittest.TestCase):
    """ Test Cases for Customer Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Customer.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

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

    def test_add_a_customer(self):
        """ Create a customer and add it to the database """
        customers = Customer.all()
        self.assertEqual(customers, [])
        customer = Customer(username="LYC", 
                            password="123", 
                            first_name="Yongchang", 
                            last_name="Liu",
                            addresses=(["WWH"]))

        self.assertTrue(customer != None)
        self.assertEqual(customer.id, None)
        customer.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(customer.id, 1)
        customers = Customer.all()
        self.assertEqual(len(customers), 1)

    def test_serialize_a_customer(self):
        """Test serialization of a Customer"""
        customer = CustomerFactory()
        data = customer.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], customer.id)
        self.assertIn("username", data)
        self.assertEqual(data["username"], customer.username)
        self.assertIn("password", data)
        self.assertEqual(data["password"], customer.password)
        self.assertIn("first_name", data)
        self.assertEqual(data["first_name"], customer.first_name)
        self.assertIn("last_name", data)
        self.assertEqual(data["last_name"], customer.last_name)
        self.assertIn("addresses", data)
        self.assertEqual(data["addresses"], customer.addresses)

    def test_deserialize_a_customer(self):
        """Test deserialize a Customer"""
        data = {
            "id": 1,
            "username": "deserialize",
            "password": "123",
            "first_name": "Yongchang",
            "last_name": "Liu",
            "addresses":(["WWH"])
        }
        customer = Customer()
        customer.deserialize(data)
        self.assertNotEqual(customer, None)
        self.assertEqual(customer.id, None)
        self.assertEqual(customer.username, "deserialize")
        self.assertEqual(customer.password, "123")
        self.assertEqual(customer.first_name, "Yongchang")
        self.assertEqual(customer.last_name, "Liu")
        self.assertEqual(customer.addresses, (["WWH"]))

    def test_deserialize_missing_data(self):
        """Test deserialize a customer with missing data"""
        data = {"id": 1, "name": "123"}
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_bad_addresses(self):
        """Test deserialize a customer with an invalid type for addresses"""
        data = {
            "id": 1,
            "username": "deserialize",
            "password": "123",
            "first_name": "Yongchang",
            "last_name": "Liu",
            "addresses": [[]]
        }
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.deserialize, data)   

    def test_deserialize_bad_data(self):
        """Test deserialize bad data"""
        data = "this is not a dictionary"
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_find_customer(self):
        """ Find a Customer by ID """
        customers = CustomerFactory.create_batch(3)
        for customer in customers:
            customer.create()
        logging.debug(customers)
        # make sure they got updated
        self.assertEqual(len(Customer.all()), 3)
        # find the 2nd customer in the list
        customer = Customer.find(customers[1].id)
        self.assertIsNot(customer, None)
        self.assertEqual(customer.id, customers[1].id)
        self.assertEqual(customer.username, customers[1].username)

    def test_delete_a_customer(self):
        """ Test Delete a Customer"""
        customer = CustomerFactory()
        customer.create()
        self.assertEqual(len(Customer.all()), 1)
        # delete the customer and make sure the customer is not in the database
        customer.delete()
        self.assertEqual(len(Customer.all()), 0)


    def test_update_a_customer(self):
        """Update a customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.create()
        logging.debug(customer)
        self.assertEqual(customer.id, 1)
        # Change it an save it
        customer.category = "k9"
        original_id = customer.id
        customer.update()
        self.assertEqual(customer.id, original_id)
        self.assertEqual(customer.category, "k9")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        customers = Customer.all()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].id, 1)
        self.assertEqual(customers[0].category, "k9")
