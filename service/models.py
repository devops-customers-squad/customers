"""
Models for Customer

All of the models are stored in this module
"""
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Customer(db.Model):
    """
    Class that represents a Customer
    """

    app = None

    __tablename__ = 'customer'
    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)
    addresses = db.relationship('Address', backref='customer', lazy=True, cascade="all, delete-orphan")
    locked=db.Column(db.Boolean,default=False,nullable=True)

    def __repr__(self):
        return "<Customer %r id=[%s]>" % (self.username, self.id)

    def create(self):
        """
        Creates a Customer to the database
        """
        logger.info("Creating %s", self.username)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Customer to the database
        """
        logger.info("Saving %s", self.username)
        if not self.id:
            raise DataValidationError("Customer update called with empty ID field")
        db.session.commit()

    def save(self):
        """
        Updates a Customer to the database
        """
        logger.info("Saving %s", self.username)
        db.session.commit()

    def delete(self):
        """ Removes a Customer from the data store """
        logger.info("Deleting %s", self.username)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Customer into a dictionary """

        customer_dict = {"id": self.id, 
            "username": self.username,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "addresses": [],
            "locked":self.locked
            }

        for address in self.addresses:
            address_dict = address.serialize()
            customer_dict["addresses"].append(address_dict)

        return customer_dict

    def serialize_for_lock(self):
        """ Serializes a Customer into a dictionary without id and password"""

        customer_dict = {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "addresses": [],
            "locked":self.locked
            }

        for address in self.addresses:
            address_dict = address.serialize()
            customer_dict["addresses"].append(address_dict)

        return customer_dict

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.username = data["username"]
            self.password = data["password"]
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.addresses = []
            if ("locked" in data) :
                self.locked = data["locked"]
            else:
                self.locked =False
            for address_data in data["addresses"]:
                address = Address()
                address.deserialize(address_data)
                self.addresses.append(address)

        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Customer: body of request contained bad or no data"
            ) 
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Customers in the database """
        logger.info("Processing all Customers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Customer by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a Customer by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_name(cls, username):
        """Returns all Customers with the given username

        Args:
            username (string): the username of the Customers you want to match
        """
        logger.info("Processing username query for %s ...", username)
        return cls.query.filter(cls.username == username)
    
    @classmethod
    def find_by_first_name(cls, first_name):
        """Returns all Customers with the given first name

        Args:
            first_name (string): the first name of the Customers you want to match
        """
        logger.info("Processing first name query for %s ...", first_name)
        return cls.query.filter(cls.first_name == first_name)
    
    @classmethod
    def find_by_last_name(cls, last_name):
        """Returns all Customers with the given last name

        Args:
            last_name (string): the last name of the Customers you want to match
        """
        logger.info("Processing last name query for %s ...", last_name)
        return cls.query.filter(cls.last_name == last_name)

class Address(db.Model):
    """
    Class that represents an Address
    """

    app = None

    # Table Schema
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    address_id = db.Column(db.Integer, primary_key=True)
    street_address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "<Address with id=[%s] %s, %s, %s %s, %s>" % (self.address_id, self.street_address, self.city, self.state, self.zipcode, self.country)

    def create(self):
        """
        Creates an Address to the database
        """
        logger.info("Creating address with street address %s", self.street_address)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an Address to the database
        """
        logger.info("Saving address with street address %s", self.street_address)
        if not self.address_id:
            raise DataValidationError("Address update called with empty address_id field")
        db.session.commit()

    def delete(self):
        """
        Removes an Address from the data store
        """
        logger.info("Deleting address with street address %s", self.street_address)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes an Address into a dictionary """

        return {"customer_id": self.customer_id,
            "address_id": self.address_id,
            "street_address": self.street_address,
            "city": self.city,
            "state": self.state,
            "zipcode": self.zipcode,
            "country": self.country}


    def deserialize(self, data):
        """
        Deserializes an Address from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.street_address = data["street_address"]
            self.city = data["city"]
            self.state = data["state"]
            self.zipcode = data["zipcode"]
            self.country = data["country"]

        except KeyError as error:
            raise DataValidationError(
                "Invalid Address: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Address: body of request contained bad or no data"
            ) 
        return self

    @classmethod
    def all(cls):
        """ Returns all of the Addresses in the database """
        logger.info("Processing all Addresses")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds an Address by its ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """Returns all Addresses with the given customer_id

        Args:
            customer_id (int): the customer id of the Addresses you want to match
        """
        logger.info("Processing query addresses by customer_id for %s ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id)