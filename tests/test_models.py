"""
Test cases for Customer Model

"""
import logging
import unittest
import os
from service import app
from service.models import Customer, Address, DataValidationError, db
from werkzeug.exceptions import NotFound
from tests.factories import CustomerFactory, AddressFactory

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

    def test_add_a_customer(self):
        """ Create a customer and add it to the database """
        customers = Customer.all()
        self.assertEqual(customers, [])
        customer = Customer(username="LYC", 
                            password="123", 
                            first_name="Yongchang", 
                            last_name="Liu",
                            locked=False,
                            addresses=([
                                Address(
                                    street_address="123 Test Road",
                                    city="New York",
                                    state="NY",
                                    zipcode=10053,
                                    country="United States"
                                )
                            ]))

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
        address = AddressFactory()
        address.customer_id = customer.id
        customer.addresses = [address]
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
        self.assertIn("locked", data)
        self.assertEqual(data["locked"], customer.locked)
        self.assertIn("addresses", data)
        self.assertIn("address_id", data["addresses"][0])
        self.assertEqual(data["addresses"][0]["address_id"], address.address_id)
        self.assertIn("customer_id", data["addresses"][0])
        self.assertEqual(data["addresses"][0]["customer_id"], address.customer_id)
        self.assertIn("street_address", data["addresses"][0])
        self.assertEqual(data["addresses"][0]["street_address"], address.street_address)
        self.assertIn("city", data["addresses"][0])
        self.assertEqual(data["addresses"][0]["city"], address.city)
        self.assertIn("state", data["addresses"][0])
        self.assertEqual(data["addresses"][0]["state"], address.state)
        self.assertIn("zipcode", data["addresses"][0])
        self.assertEqual(data["addresses"][0]["zipcode"], address.zipcode)
        self.assertIn("country", data["addresses"][0])
        self.assertEqual(data["addresses"][0]["country"], address.country)

    def test_deserialize_a_customer(self):
        """Test deserialize a Customer"""
        data = {
            "id": 1,
            "username": "deserialize",
            "password": "123",
            "first_name": "Yongchang",
            "last_name": "Liu",
            "locked":False,
            "addresses": [{
                "street_address": "123 Test Road",
                "city": "New York",
                "state": "NY",
                "zipcode": 10053,
                "country": "United States"
            }]
        }
        customer = Customer()
        customer.deserialize(data)
        self.assertNotEqual(customer, None)
        self.assertEqual(customer.id, None)
        self.assertEqual(customer.username, "deserialize")
        self.assertEqual(customer.password, "123")
        self.assertEqual(customer.first_name, "Yongchang")
        self.assertEqual(customer.last_name, "Liu")
        self.assertEqual(customer.locked, False)
        address = customer.addresses[0]
        self.assertEqual(address.street_address, "123 Test Road")
        self.assertEqual(address.city, "New York")
        self.assertEqual(address.state, "NY")
        self.assertEqual(address.zipcode, 10053)
        self.assertEqual(address.country, "United States")

    def test_deserialize_a_customer_without_locked(self):
        """Test deserialize a Customer without locked"""
        data = {
            "id": 1,
            "username": "deserialize",
            "password": "123",
            "first_name": "Yongchang",
            "last_name": "Liu",
            "addresses": [{
                "street_address": "123 Test Road",
                "city": "New York",
                "state": "NY",
                "zipcode": 10053,
                "country": "United States"
            }]
        }
        customer = Customer()
        customer.deserialize(data)
        self.assertNotEqual(customer, None)
        self.assertEqual(customer.id, None)
        self.assertEqual(customer.username, "deserialize")
        self.assertEqual(customer.password, "123")
        self.assertEqual(customer.first_name, "Yongchang")
        self.assertEqual(customer.last_name, "Liu")
        self.assertEqual(customer.locked, False)
        address = customer.addresses[0]
        self.assertEqual(address.street_address, "123 Test Road")
        self.assertEqual(address.city, "New York")
        self.assertEqual(address.state, "NY")
        self.assertEqual(address.zipcode, 10053)
        self.assertEqual(address.country, "United States")

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
            "locked":False,
            "addresses": [{"street_address": "123 Testing Lane"}]
        }
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.deserialize, data)   

    def test_deserialize_customer_bad_data(self):
        """Test deserialize bad customer data"""
        data = "this is not a dictionary"
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.deserialize, data)

    def test_deserialize_address_bad_data(self):
        """Test deserialize bad address data"""
        data = "this is not a dictionary"
        address = AddressFactory()
        self.assertRaises(DataValidationError, address.deserialize, data)

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
        print("ADDRESS", customer.addresses)
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
        customer.username = "nyu_student"
        original_id = customer.id
        customer.update()
        self.assertEqual(customer.id, original_id)
        self.assertEqual(customer.username, "nyu_student")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        customers = Customer.all()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].id, 1)
        self.assertEqual(customers[0].username, "nyu_student")

    def test_add_an_address(self):
        """ Create an address and add it to the database """
        customer = CustomerFactory()
        customer.create()
        self.assertEqual(len(customer.addresses), 0)
        addresses = Address.all()
        self.assertEqual(addresses, [])
        address = Address(street_address="123 Test Road",
                            city="New York",
                            state="NY",
                            zipcode=10053,
                            country="United States"
                        )
        address.customer_id = customer.id
        address.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(address.address_id, 1)
        addresses = Address.all()
        self.assertEqual(len(addresses), 1)
        self.assertEqual(len(customer.addresses), 1)

    def test_find_address(self):
        """ Find an Address by address_id """
        customers = CustomerFactory.create_batch(3)
        for customer in customers:
            customer.create()
            address = AddressFactory()
            address.customer_id = customer.id
            address.create()
        addresses = Address.all()
        logging.debug(addresses)
        self.assertEqual(len(addresses), 3)
        # find the 2nd customer in the list
        address = Address.find(addresses[1].address_id)
        self.assertIsNot(address, None)
        self.assertEqual(address.address_id, addresses[1].address_id)
        self.assertEqual(address.street_address, addresses[1].street_address)

    def test_delete_an_address(self):
        """ Test Delete an Address"""
        customer = CustomerFactory()
        customer.create()
        address = AddressFactory()
        address.customer_id = customer.id
        address.create()
        self.assertEqual(len(Address.all()), 1)
        # delete the customer and make sure the customer is not in the database
        address.delete()
        self.assertEqual(len(Address.all()), 0)
        self.assertEqual(len(customer.addresses), 0)

    def test_update_a_customer(self):
        """Update an Address"""
        customer = CustomerFactory()
        customer.create()
        address = AddressFactory()
        logging.debug(address)
        address.customer_id = customer.id
        address.create()
        logging.debug(address)
        print(address)
        # Change it and save it
        address.street_address = "%!#"
        original_id = address.address_id
        address.update()
        self.assertEqual(address.address_id, original_id)
        self.assertEqual(address.street_address, "%!#")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        addresses = Address.all()
        self.assertEqual(len(addresses), 1)
        self.assertEqual(addresses[0].address_id, original_id)
        self.assertEqual(addresses[0].street_address, "%!#")
        # Check that change is reflected in customer
        self.assertEqual(len(customer.addresses), 1)
        self.assertEqual(customer.addresses[0].street_address, "%!#")

    def test_find_address_by_customer_id(self):
        """ Find an Address by its customer_id """
        batch_size = 3
        address_num = 2
        customers = CustomerFactory.create_batch(batch_size)
        for customer in customers:
            customer.create()
            for _ in range(address_num):
                address = AddressFactory()
                address.customer_id = customer.id
                address.create()
        # make sure expected number of addresses got created
        self.assertEqual(len(Address.all()), batch_size * address_num)
        # filter by id of the the 2nd customer in the list
        addresses = Address.find_by_customer_id(customers[1].id).all()
        self.assertEqual(len(addresses), address_num)
    
    def test_find_by_first_name(self):
        """ Find All Customers with the given first name"""
        all_name = ["user1", "user2", "user3"]
        all_password = ["1234", "abcd", "efgh"]
        batch_size = 3
        address_num = 2
        customers = CustomerFactory.create_batch(batch_size)
        for i, customer in enumerate(customers):
            customer.create()
            customer.username = all_name[i]
            customer.password = all_password[i]
            if i < 2:
              customer.first_name = "John"
            for _ in range(address_num):
                address = AddressFactory()
                address.customer_id = customer.id
                address.create()
       
        customers = Customer.find_by_first_name("John").all()
        self.assertEqual(customers[0].username, "user1")
        self.assertEqual(customers[1].username, "user2")
        self.assertEqual(customers[0].password, "1234")
        self.assertEqual(customers[1].password, "abcd")
    
    def test_find_by_last_name(self):
        """ Find All Customers with the given last name"""
        all_name = ["user1", "user2", "user3"]
        all_password = ["1234", "abcd", "efgh"]
        batch_size = 3
        address_num = 2
        customers = CustomerFactory.create_batch(batch_size)
        for i, customer in enumerate(customers):
            customer.create()
            customer.username = all_name[i]
            customer.password = all_password[i]
            if i < 2:
              customer.last_name = "John"
            for _ in range(address_num):
                address = AddressFactory()
                address.customer_id = customer.id
                address.create()
       
        customers = Customer.find_by_last_name("John").all()
        self.assertEqual(customers[0].username, "user1")
        self.assertEqual(customers[1].username, "user2")
        self.assertEqual(customers[0].password, "1234")
        self.assertEqual(customers[1].password, "abcd")
    
    def test_find_by_username(self):
        """ Find All Customers with the given username"""
        batch_size = 3
        address_num = 2
        customers = CustomerFactory.create_batch(batch_size)
        for customer in customers:
            customer.create()
            for _ in range(address_num):
                address = AddressFactory()
                address.customer_id = customer.id
                address.create()
        test_user = customers[0]
        customers = Customer.find_by_name(test_user.username).all()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].first_name, test_user.first_name)
    
    
    
    

    def test_lock_a_customer(self):
        """Lock a customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.create()
        logging.debug(customer)
        self.assertEqual(customer.id, 1)
        # Change it an save it
        customer.locked = True
        original_id = customer.id
        customer.update()
        self.assertEqual(customer.id, original_id)
        self.assertEqual(customer.locked, True)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        customers = Customer.all()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].id, 1)
        self.assertEqual(customers[0].locked, True)
