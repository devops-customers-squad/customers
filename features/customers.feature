Feature: The customer store service back-end
    As a Store Owner
    I need a RESTful customer service
    So that I can keep track of all my customers
Background:
    Given the following customers 
        | username | password | first_name | last_name | street_address| city        | state       | zipcode | country |
        | user1   | 1234     | Henry      | George    | 123           | New York    | NY          | 10000   | USA     |
        | user2   | 1235     | John       | Georgie   | 234           | Boston      | Massachusat | 20000   | USA     |
        | user3   | 1236     | Tom        | Giovani   | 345           | White plain | NY          | 10567   | USA     |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customers RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a customer with same username
    When I visit the "Home Page"
    And I set the "username" to "user1"
    And I set the "password" to "1111"
    And I set the "first_name" to "jiraphon"
    And I press the "Create Customer" button
    Then I should see the message "Username 'user1' already exists."

Scenario: Create a customer with Invalid address
    When I visit the "Home Page"
    And I set the "username" to "dome"
    And I set the "password" to "1111"
    And I set the "first_name" to "jiraphon"
    And I set the "last_name" to "yenphraphai"
    And I set the "street_address" to "1234"
    And I press the "Create Customer" button
    Then I should see the message "Invalid Address: missing city"
    
Scenario: Create a customer with valid information
    When I visit the "Home Page"
    And I set the "username" to "dome"
    And I set the "password" to "1111"
    And I set the "first_name" to "jiraphon"
    And I set the "last_name" to "yenphraphai"
    And I set the "street_address" to "1234"
    And I set the "city" to "New York"
    And I set the "state" to "NY"
    And I set the "zip" to "10090"
    And I set the "country" to "USA"
    And I press the "Create Customer" button
    Then I should see the message "Success"



