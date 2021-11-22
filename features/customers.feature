Feature: The customer store service back-end
    As a Store Owner
    I need a RESTful customer service
    So that I can keep track of all my customers
Background:
    Given the following customers 
        | username | password | first_name | last_name | street_address| city        | state         | zipcode | country |
        | user1   | 1234     | Henry      | George    | 123           | New York     | NY            | 10000   | USA     |
        | user2   | 1235     | John       | Georgie   | 234           | Boston       | Massachusetts | 20000   | USA     |
        | user3   | 1236     | Tom        | Giovani   | 345           | White Plains | NY            | 10567   | USA     |
        | user4   | 1236     | Tim        | Giovani   | None          | None         | None          | None    | None    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customers RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a customer with same username
    When I visit the "Home Page"
    And I set the "Username" to "user1"
    And I set the "Password" to "1111"
    And I set the "First Name" to "jiraphon"
    And I set the "Last Name" to "jiraphon"
    And I press the "Create Customer" button
    Then I should see the message "Username 'user1' already exists."

Scenario: Create a customer with Invalid address
    When I visit the "Home Page"
    And I set the "Username" to "dome"
    And I set the "Password" to "1111"
    And I set the "First Name" to "jiraphon"
    And I set the "Last Name" to "yenphraphai"
    And I set the "Street Address" to "1234"
    And I press the "Create Customer" button
    Then I should see the message "Invalid Address: missing city"
    
Scenario: Create a customer with valid information
    When I visit the "Home Page"
    And I set the "Username" to "dome"
    And I set the "Password" to "1111"
    And I set the "First Name" to "jiraphon"
    And I set the "Last Name" to "yenphraphai"
    And I set the "Street Address" to "1234"
    And I set the "City" to "New York"
    And I set the "State" to "NY"
    And I set the "Zip" to "10090"
    And I set the "Country" to "USA"
    And I press the "Create Customer" button
    Then I should see the message "Success"

Scenario: Read a customer without an address
    When I visit the "Home Page"
    And I set the "First Name" to "Tim"
    And I press the "Search for Customer" button
    And I clear the "First Name" field
    And I clear the "Last Name" field
    And I clear the "Username" field
    And I clear the "Password" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Tim" in the "First Name" field
    And I should see "Giovani" in the "Last Name" field
    And I should see "user4" in the "Username" field
    And I should see "1236" in the "Password" field
    And I should see "false" in the "Locked" field
    And the "Street Address" field should be empty
    And the "City" field should be empty
    And the "State" field should be empty
    And the "Country" field should be empty
    And the "Zip" field should be empty
    And I should see "user4" in the customer results
    And I should not see "user1" in the customer results
    And I should not see "user2" in the customer results
    And I should not see "user3" in the customer results

Scenario: Read a customer with an address
    When I visit the "Home Page"
    And I set the "First Name" to "John"
    And I press the "Search for Customer" button
    And I clear the "First Name" field
    And I clear the "Last Name" field
    And I clear the "Username" field
    And I clear the "Password" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "John" in the "First Name" field
    And I should see "Georgie" in the "Last Name" field
    And I should see "user2" in the "Username" field
    And I should see "1235" in the "Password" field
    And I should see "false" in the "Locked" field
    And I should see "234" in the "Street Address" field
    And I should see "Boston" in the "City" field
    And I should see "Massachusetts" in the "State" field
    And I should see "USA" in the "Country" field
    And I should see "20000" in the "Zip" field
    And I should see "user2" in the customer results
    And I should not see "user1" in the customer results
    And I should not see "user3" in the customer results
    And I should not see "user4" in the customer results

Scenario: Read a customer with an invalid ID
    When I visit the "Home Page"
    And I set the "Customer ID" to "100000"
    And I press the "Retrieve" button
    Then I should see the message "Customer with id '100000' was not found."

Scenario: List all customers
    When I visit the "Home Page"
    And I press the "Search for Customer" button
    Then I should see the message "Success"
    And I should see "user1" in the customer results
    And I should see "user2" in the customer results
    And I should see "user3" in the customer results
    And I should see "user4" in the customer results

Scenario: Lock a customer
    When I visit the "Home Page"
    And I set the "First Name" to "John"
    And I press the "Search for Customer" button
    Then I should see "false" in the "Locked" field
    When I press the "Lock" button
    Then I should see the message "Success"
    And I should see "true" in the "Locked" field
    And I should see "John" in the "First Name" field
    And I should see "Georgie" in the "Last Name" field
    And I should see "user2" in the "Username" field
    And I should see "1235" in the "Password" field
    And I should not see "user1" in the customer results
    And I should not see "user2" in the customer results
    And I should not see "user3" in the customer results
    And I should not see "user4" in the customer results
    # Check that the Locked field is now set to true when the customer is retrieved
    When I visit the "Home Page"
    And I set the "First Name" to "John"
    And I press the "Search for Customer" button
    Then I should see "true" in the "Locked" field

Scenario: Delete a customer with no id provided
    When I visit the "Home Page"
    And I press the "Delete" button
    Then I should see the message "Server error!"

Scenario: Delete a customer with id provided
    When I visit the "Home Page"    
    And I set the "First Name" to "John"
    And I press the "Search for Customer" button
    When I press the "Delete" button
    Then I should see the message "Customer has been Deleted!"
    When I press the "Search for Customer" button
    Then I should see the message "Success"
    And I should see "user1" in the customer results
    And I should not see "user2" in the customer results
    And I should see "user3" in the customer results
    And I should see "user4" in the customer results

Scenario: Unlock a customer after locking
    When I visit the "Home Page"
    And I set the "First Name" to "Henry"
    And I press the "Search for Customer" button
    Then I should see "false" in the "Locked" field
    When I press the "Lock" button
    Then I should see "true" in the "Locked" field
    # Unlock the locked customer
    When I press the "Unlock" button
    Then I should see the message "Success"
    And I should see "false" in the "Locked" field
    And I should see "Henry" in the "First Name" field
    And I should see "George" in the "Last Name" field
    And I should see "user1" in the "Username" field
    And I should see "1234" in the "Password" field
    And I should not see "user1" in the customer results
    And I should not see "user2" in the customer results
    And I should not see "user3" in the customer results
    And I should not see "user4" in the customer results
