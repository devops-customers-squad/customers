# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""
from os import stat_result
import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from service.models import Customer, Address
import string
import random

class AddressFactory(factory.Factory):
    """ Creates fake addresses that you don't have to feed """

    class Meta:
      model = Address

    address_id = factory.Sequence(lambda n: n)
    street_address = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state")
    zipcode = FuzzyInteger(10000, 99999)
    country = factory.Faker("country")

class CustomerFactory(factory.Factory):
    """ Creates fake customers that you don't have to feed """

    class Meta:
      model = Customer

    id = factory.Sequence(lambda n: n)
    #username = factory.Faker("first_name") # shouldn't have duplicated username by doing this
    username = factory.Sequence(lambda n: str(factory.Faker("first_name")) + f" {n}") # prevent duplicate username
    password = FuzzyChoice(choices=[x for x in string.ascii_lowercase])
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    locked=False
    addresses = []