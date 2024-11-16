# ********RoostGPT********

# Test generated by RoostGPT for test karate-integration-credential using AI Type  and AI Model 
# 
# ROOST_METHOD_HASH=e8010dc6d7
# ROOST_METHOD_SIG_HASH=3a429a7e0a
# 
#  ########## Scenario ########## 
# 
# {
#   feature: 'Feature: Credential Wallet API\r\n' +
#     '  As a user of the Credential Wallet API\r\n' +
#     '  I want to be able to perform CRUD operations on accounts\r\n' +
#     '  So that I can manage my account effectively',
#   background: 'Background:\r\n    Given the base URL is "http://localhost:8080"',
#   rule: null,
#   scenario: {
#     title: 'Scenario: Create my account',
#     steps: 'When the client sends a POST request "/accounts" with the accounts_body payload\r\n' +
#       'Then create an account with the specified informatio\r\n' +
#       'And verify the account created using GET request for "/me"',
#     examples: ''
#   }
# }
# 

# ********RoostGPT********
Feature: Credential Wallet API
  As a user of the Credential Wallet API
  I want to be able to perform CRUD operations on accounts
  So that I can manage my account effectively

  Background:
    * url 'http://localhost:8080'

  Scenario: Create my account
    Given path '/accounts'
    When method post
    And request
      """
      { 
        "name": "John Doe", 
        "email": "john.doe@example.com", 
        "password": "password123" 
      }
      """
    Then status 201
    And match response == '#object'
    And match response.id == '#number'
    And match response.name == 'John Doe'
    And match response.email == 'john.doe@example.com'
    And match response.path == '/accounts'

  Scenario: Verify the account created
    Given path '/me'
    When method get
    Then status 200
    And match response == '#object'
    And match response.id == '#number'
    And match response.name == 'John Doe'
    And match response.email == 'john.doe@example.com'
    And match response.path == '/me'
