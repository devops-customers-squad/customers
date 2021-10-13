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

def init_db(app):
    """Initialies the SQLAlchemy app"""
    Customer.init_db(app)
    
class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class Customer(db.Model):
    """
    Class that represents a Customer
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)
    addresses = db.Column(db.ARRAY(db.String(100)), nullable=False)

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
        return {"id": self.id, "username": self.username,"password":self.password,"first_name":self.first_name,"last_name":self.last_name,"addresses":self.addresses}

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id=data["id"]
            self.username = data["username"]
            self.password=data["password"]
            self.first_name=data["first_name"]
            self.last_name=data["last_name"]
            self.addresses=data["addresses"]
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
