Feature: The wishlist service back-end
    As a e-Commerce Website
    I need a RESTful wishlist service
    So that I can keep track of all users' wishlists and their contents

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
