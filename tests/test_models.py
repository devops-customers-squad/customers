"""
Test cases for YourResourceModel Model

"""
import logging
import unittest
import os
from service import app
from service.models import Customer, DataValidationError, db
from werkzeug.exceptions import NotFound
from tests.factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  CUSTOMER   M O D E L   T E S T   C A S E S
######################################################################
class TestYourResourceModel(unittest.TestCase):
    """ Test Cases for YourResourceModel Model """

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

    #def test_create_a_pet(self):
    #    """ Create a customer and assert that it exists """
    #    customer = Customer(username="LYC", password="123", first_name="Yongchang", last_name="Liu",addresses=[["WWH"]])
    #   self.assertTrue(customer != None)
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
        customer = Customer(username="LYC", password="123", first_name="Yongchang", last_name="Liu",addresses=(["WWH"]))
        self.assertTrue(customer != None)
        self.assertEqual(customer.id, None)
        customer.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(customer.id, 1)
        customers = Customer.all()
        self.assertEqual(len(customers), 1)