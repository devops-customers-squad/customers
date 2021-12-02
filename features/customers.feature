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
    Then I should see the message "Invalid Customer Address: missing city"
    
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

Scenario: Clear customer information
    When I visit the "Home Page"
    And I set the "First Name" to "Tom"
    And I press the "Search for Customer" button
    And I press the "Clear All" button
    Then the "Customer ID" field should be empty
    And the "First Name" field should be empty
    And the "Last Name" field should be empty
    And the "Username" field should be empty
    And the "Password" field should be empty
    And the "Locked" field should be empty
    And the "Address ID" field should be empty
    And the "Street Address" field should be empty
    And the "City" field should be empty
    And the "State" field should be empty
    And the "Country" field should be empty
    And the "Zip" field should be empty
    And I should not see "user4" in the customer results
    And I should not see "user1" in the customer results
    And I should not see "user2" in the customer results
    And I should not see "user3" in the customer results

Scenario: Read a customer without an address
    When I visit the "Home Page"
    And I set the "First Name" to "Tim"
    And I press the "Search for Customer" button
    And I copy the "Customer ID" field
    And I press the "Clear All" button
    And I paste the "Customer ID" field
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
    And I copy the "Customer ID" field
    And I press the "Clear All" button
    And I paste the "Customer ID" field
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

Scenario: Update a customer
    When I visit the "Home Page"
    And I set the "First Name" to "Tim"
    And I set the "Last Name" to "Giovani"
    And I press the "Search for Customer" button
    Then I should see the message "Success"
    And I should see "Tim" in the "First Name" field
    And I should see "Giovani" in the "Last Name" field

    # Update this cusotmer
    When I copy the "Customer ID" field
    And I press the "Clear All" button
    And I paste the "Customer ID" field
    And I set the "First Name" to "Tina"
    And I set the "Last Name" to "Li"
    And I set the "Username" to "Tina_username"
    And I set the "Password" to "Tina_password"
    And I press the "Update Customer" button
    Then I should see the message "Success"
    And I should see "Tina" in the "First Name" field
    And I should see "Li" in the "Last Name" field
    And I should see "Tina_username" in the "Username" field
    And I should see "Tina_password" in the "Password" field

Scenario: Update a customer with empty strings
    When I visit the "Home Page"
    And I set the "Username" to "user1"
    And I press the "Search for Customer" button

    # Update this cusotmer with empty first Name
    And I set the "First Name" to ""
    And I press the "Update Customer" button
    Then I should see the message "Invalid Customer update: missing first_name"

    # Update this cusotmer with empty last Name
    When I press the "Retrieve" button
    And I set the "Last Name" to ""
    And I press the "Update Customer" button
    Then I should see the message "Invalid Customer update: missing last_name"

    # Update this cusotmer with empty username
    When I press the "Retrieve" button
    And I set the "Username" to ""
    And I press the "Update Customer" button
    Then I should see the message "Invalid Customer update: missing username"

    # Update this cusotmer with empty password
    When I press the "Retrieve" button
    And I set the "Password" to ""
    And I press the "Update Customer" button
    Then I should see the message "Invalid Customer update: missing password"

Scenario: Lock a customer
    When I visit the "Home Page"
    And I set the "First Name" to "John"
    And I press the "Search for Customer" button
    Then I should see "false" in the "Locked" field
    When I copy the "Customer ID" field
    And I press the "Clear All" button
    And I paste the "Customer ID" field
    And I press the "Lock" button
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
    And I copy the "Customer ID" field
    And I press the "Clear All" button
    And I paste the "Customer ID" field
    And I press the "Delete" button
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
    When I copy the "Customer ID" field
    And I press the "Clear All" button
    And I paste the "Customer ID" field
    And I press the "Lock" button
    Then I should see "true" in the "Locked" field
    # Unlock the locked customer
    When I copy the "Customer ID" field
    And I press the "Clear All" button
    And I paste the "Customer ID" field
    And I press the "Unlock" button
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

Scenario: Query a customer by state
    When I visit the "Home Page"
    And I set the "Username" to "user1"
    And I press the "Search for Customer" button
    And I press the "Clear Address" button
    And I set the "State" to "NY"
    And I press the "Search for Customer Addresses" button
    Then I should see the message "Success"
    And I should see "123" in the "Street Address" field
    And I should see "New York" in the "City" field
    And I should see "NY" in the "State" field
    And I should see "USA" in the "Country" field
    And I should see "10000" in the "Zip" field

Scenario: Query a customer by zipcode
    When I visit the "Home Page"
    And I set the "Username" to "user1"
    And I press the "Search for Customer" button
    And I press the "Clear Address" button
    And I set the "Zip" to "10000"
    And I press the "Search for Customer Addresses" button
    Then I should see the message "Success"
    And I should see "123" in the "Street Address" field
    And I should see "New York" in the "City" field
    And I should see "NY" in the "State" field
    And I should see "USA" in the "Country" field
    And I should see "10000" in the "Zip" field

Scenario: Query a customer by country
    When I visit the "Home Page"
    And I set the "Username" to "user1"
    And I press the "Search for Customer" button
    And I press the "Clear Address" button
    And I set the "Country" to "USA"
    And I press the "Search for Customer Addresses" button
    Then I should see the message "Success"
    And I should see "123" in the "Street Address" field
    And I should see "New York" in the "City" field
    And I should see "NY" in the "State" field
    And I should see "USA" in the "Country" field
    And I should see "10000" in the "Zip" field

Scenario: Query a customer by stree_address
    When I visit the "Home Page"
    And I set the "Username" to "user1"
    And I press the "Search for Customer" button
    And I press the "Clear Address" button
    And I set the "Street Address" to "123"
    And I press the "Search for Customer Addresses" button
    Then I should see the message "Success"
    And I should see "123" in the "Street Address" field
    And I should see "New York" in the "City" field
    And I should see "NY" in the "State" field
    And I should see "USA" in the "Country" field
    And I should see "10000" in the "Zip" field

Scenario: Query a customer by city
    When I visit the "Home Page"
    And I set the "Username" to "user2"
    And I press the "Search for Customer" button
    And I press the "Clear Address" button
    And I set the "City" to "Boston"
    And I press the "Search for Customer Addresses" button
    Then I should see the message "Success"
    And I should see "234" in the "Street Address" field
    And I should see "Boston" in the "City" field
    And I should see "Massachusetts" in the "State" field
    And I should see "USA" in the "Country" field
    And I should see "20000" in the "Zip" field

Scenario: Update customer address
    When I visit the "Home Page"
    And I set the "Username" to "user2"
    And I press the "Search for Customer" button

    # Update the address
    And I set the "Street Address" to "That Street"
    And I set the "City" to "New Jersey"
    And I set the "State" to "NJ"
    And I set the "Country" to "America"
    And I set the "Zip" to "11111"
    And I press the "Update Customer Address" button
    Then I should see the message "Success"
    When I press the "Retrieve Address" button
    Then I should see "That Street" in the "Street Address" field
    And I should see "New Jersey" in the "City" field
    And I should see "NJ" in the "State" field
    And I should see "America" in the "Country" field
    And I should see "11111" in the "Zip" field