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
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Customer
import string


class CustomerFactory(factory.Factory):
    """ Creates fake pets that you don't have to feed """

    class Meta:
      model = Customer

    id = factory.Sequence(lambda n: n)
    username = FuzzyChoice(choices=[x for x in string.ascii_lowercase])
    password = FuzzyChoice(choices=[x for x in range(9)])
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    addresses = FuzzyChoice(choices=["Bangkok", "New York", "Beijing"])