Feature: API Testing for Application Functionality

Background:
  Given the API base URL 'http://api.example.com'
  And the authorization header is set
  And the content type is 'application/json'

Scenario: User login with ID number and secret code
  Given a registered user with ID '123456789' and a secret code received via SMS
  When I send a POST request to '/login' with payload:
    | id_number  | secret_code |
    | 123456789  | 987654      |
  Then the response status should be 200
  And the response should contain the user's dashboard

Scenario: User login using biometric authentication
  Given a user has configured biometric authentication on their device
  When I send a POST request to '/biometric-login'
  Then the response status should be 200
  And the response should contain the user's dashboard

Scenario: Automatic lock after 3 failed login attempts
  Given a registered user with ID '123456789'
  When I send a POST request to '/login' with invalid credentials three times
    | id_number  | secret_code |
    | 123456789  | 123456      |
    | 123456789  | 123456      |
    | 123456789  | 123456      |
  Then the response status should be 403
  And the response should contain 'Account locked due to multiple failed attempts'

Scenario: Viewing account details
  Given a user with account activity in the system
  When I send a GET request to '/account-details'
  Then the response status should be 200
  And the response should include 'balance' and 'transaction details for the last 90 days'

Scenario: Transfer funds to an internal account
  Given a user with sufficient balance
  When I send a POST request to '/transfer' with payload:
    | to_account | amount |
    | 987654321  | 1000   |
  Then the response status should be 200
  And the response should contain 'Funds transferred successfully'

Scenario: System availability
  Given the system is deployed and operational
  When I monitor the system for 30 consecutive days
  Then the availability percentage should be at least 99.5%

Scenario: Performance – Response time for each action
  Given the system is deployed and operational
  When I perform various actions in the application (login, view account details, transfers)
  Then the response time for each action should not exceed 2 seconds
