Feature: The wishlist service back-end
    As a e-Commerce Website
    I need a RESTful wishlist service
    So that I can keep track of all users' wishlists and their contents

Background:
    Given the following wishlists
        | customer_id | name           |
        | 128         | yesterday      |
        | 256         | today          |
        | 512         | tomorrow       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlist RESTful Service" in the title
    And I should not see "404 Not Found"
    
Scenario: Create a Wishlist
    Given The service is running
    When I visit the "home page"
    And I set the "Wishlist Name - Create" to "WISHLIST"
    And I set the "Customer ID - Create" to "10"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Wishlist ID - Create" field
    And I press the "Clear" button
    Then the "Wishlist ID - Search" field should be empty
    And the "Wishlist Name - Search" field should be empty
    And the "Customer ID - Search" field should be empty
    When I paste the "Wishlist ID - Search" field
    And I press the "Search" button
    Then I should see "1" wishlist(s)
    And I should see Name = "WISHLIST", Customer ID = "10" in the results

Scenario: Add item to a Wishlist
    Given The service is running
    When I visit the "home page"
    And I set the "Wishlist Name - Create" to "WISHLIST"
    And I set the "Customer ID - Create" to "10"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Wishlist ID - Create" field
    And I press the "Clear" button
    And I press the "Wishlist Item" tab
    When I paste the "Wishlist ID - Create Product" field
    And I set the "Product ID - Create Product" to "1024"
    And I set the "Product Name - Create Product" to "Powers of 2"
    And I press the "Create - Product" button
    Then I should see the message "Success"
    When I press the "Clear - Product" button
    Then the "Wishlist ID - Search Product" field should be empty
    And the "Product ID - Search Product" field should be empty
    And the "Product Name - Search Product" field should be empty
    When I paste the "Wishlist ID - Search Product" field
    And I set the "Product ID - Search Product" to "1024"
    And I press the "Search - Product" button
    Then I should see "1" product(s)
    And I should see Product ID = "1024", Product Name = "Powers of 2" in the results

Scenario: Delete a Wishlist
    Given The service is running
    When I visit the "home page"
    And I set the "Wishlist Name - Create" to "WISHLIST"
    And I set the "Customer ID - Create" to "10"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Wishlist ID - Create" field
    And I press the "Clear" button
    When I paste the "Wishlist ID - Delete" field
    And I press the "Delete" button
    Then I should see the message "Wishlist has been Deleted!"

Scenario: Delete a Wishlist Item
    Given The service is running
    When I visit the "home page"
    And I set the "Wishlist Name - Create" to "WISHLIST"
    And I set the "Customer ID - Create" to "10"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Wishlist ID - Create" field
    And I press the "Clear" button
    And I press the "Wishlist Item" tab
    When I paste the "Wishlist ID - Create Product" field
    And I set the "Product ID - Create Product" to "1024"
    And I set the "Product Name - Create Product" to "Powers of 2"
    And I press the "Create - Product" button
    Then I should see the message "Success"
    When I paste the "Wishlist ID - Delete Product" field
    And I set the "Product ID - Delete Product" to "1024"
    And I press the "Delete - Product" button
    Then I should see the message "Wishlist Product has been Deleted!"

Scenario: Update a Wishlist
    When I visit the "Home Page"
    And I set the "Customer ID - Search" to "128"
    And I set the "Wishlist Name - Search" to "yesterday"
    And I press the "Search" button
    Then I should see Name = "yesterday", Customer ID = "128" in the results
    When I copy the first result
    And I paste the "Wishlist ID - Update" field
    And I change "Wishlist Name - Update" to "before today"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Wishlist Id - Update" field
    And I press the "Clear" button
    And I paste the "Wishlist Id - Search" field
    And I press the "Search" button
    Then I should see Name = "before today", Customer ID = "128" in the results

Scenario: List all Wishlists
    Given The service is running
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see Name = "yesterday", Customer ID = "128" in the results
    Then I should see Name = "today", Customer ID = "256" in the results
    Then I should see Name = "tomorrow", Customer ID = "512" in the results
    Then I should see "3" wishlist(s)

Scenario: Get a Wishlist Item
    Given The service is running
    When I visit the "home page"
    And I set the "Wishlist Name - Create" to "WISHLIST"
    And I set the "Customer ID - Create" to "10"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Wishlist ID - Create" field
    And I press the "Clear" button
    And I press the "Wishlist Item" tab
    When I paste the "Wishlist ID - Create Product" field
    And I set the "Product ID - Create Product" to "1024"
    And I set the "Product Name - Create Product" to "Powers of 2"
    And I press the "Create - Product" button
    Then I should see the message "Success"
    When I paste the "Wishlist ID - Search Product" field
    And I set the "Product ID - Search Product" to "1024"
    And I press the "Search - Product" button
    Then I should see Product ID = "1024", Product Name = "Powers of 2" in the results
