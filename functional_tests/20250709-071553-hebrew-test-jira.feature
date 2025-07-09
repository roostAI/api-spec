Feature: API Testing for Banking Application

Background:
  Given the API base URL 'http://api.bankjerusalem.com'
  And the authorization header is set
  And the content type is 'application/json'

Scenario: Successful login with ID and secret code
  Given the user ID is '123456789'
  And the secret code is 'correctCode'
  When I send a POST request to '/login' with the payload
    | userId     | secretCode  |
    | 123456789  | correctCode |
  Then the response status should be 200
  And the response should contain 'login successful'

Scenario: Account lock after three failed login attempts
  Given the user ID is '123456789'
  And the secret code is 'wrongCode'
  When I send a POST request to '/login' with the payload
    | userId     | secretCode |
    | 123456789  | wrongCode  |
  Then the response status should be 401
  And the response should contain 'invalid credentials'
  When I repeat this request 3 times
  Then the account should be locked
  And the response should contain 'account locked'

Scenario: Successful login using biometric authentication
  Given the user has biometric authentication enabled
  When I send a POST request to '/login/biometric' with the payload
    | biometricData | validFingerprint |
  Then the response status should be 200
  And the response should contain 'login successful'

Scenario: Viewing recent login information
  When I send a GET request to '/login/history'
  Then the response status should be 200
  And the response should contain 'recent login details'

Scenario: Viewing account balance
  When I send a GET request to '/account/balance'
  Then the response status should be 200
  And the response should contain 'account balance details'

Scenario: Viewing transaction details for the last 90 days with date filter
  When I send a GET request to '/transactions?startDate=2023-01-01&endDate=2023-03-31'
  Then the response status should be 200
  And the response should contain 'filtered transaction details'

Scenario: Viewing transactions by type
  When I send a GET request to '/transactions?type=credit'
  Then the response status should be 200
  And the response should contain 'credit transaction details'

Scenario: Viewing account number and branch ID
  When I send a GET request to '/account/details'
  Then the response status should be 200
  And the response should contain 'account number and branch ID'

Scenario: Internal bank transfer
  Given the recipient account is '987654321'
  And the amount is '1000'
  When I send a POST request to '/transfer/internal' with the payload
    | recipientAccount | amount |
    | 987654321        | 1000   |
  Then the response status should be 200
  And the response should contain 'transfer successful'

Scenario: External bank transfer
  Given the recipient account is '123456789'
  And the amount is '2000'
  When I send a POST request to '/transfer/external' with the payload
    | recipientAccount | amount |
    | 123456789        | 2000   |
  Then the response status should be 200
  And the response should contain 'transfer successful'

Scenario: Adding a new beneficiary after SMS verification
  Given the beneficiary details are provided
  And SMS verification code is '123456'
  When I send a POST request to '/beneficiary/add' with the payload
    | beneficiaryDetails | verificationCode |
    | details            | 123456           |
  Then the response status should be 200
  And the response should contain 'beneficiary added successfully'

Scenario: Scheduling a future transfer
  Given the transfer date is '2023-12-25'
  And the amount is '500'
  When I send a POST request to '/transfer/schedule' with the payload
    | transferDate | amount |
    | 2023-12-25   | 500    |
  Then the response status should be 200
  And the response should contain 'transfer scheduled successfully'

Scenario: Viewing available credit balance
  When I send a GET request to '/credit/balance'
  Then the response status should be 200
  And the response should contain 'available credit balance'

Scenario: Viewing future credit card charges
  When I send a GET request to '/credit/future-charges'
  Then the response status should be 200
  And the response should contain 'future charges details'

Scenario: Temporary or permanent card blocking
  Given the card ID is '1234-5678-9012-3456'
  When I send a POST request to '/card/block' with the payload
    | cardId             | blockType |
    | 1234-5678-9012-3456| temporary |
  Then the response status should be 200
  And the response should contain 'card blocked successfully'

Scenario: Requesting a new card issuance
  Given the user requests a new card
  When I send a POST request to '/card/issue'
  Then the response status should be 200
  And the response should contain 'new card request submitted successfully'

Scenario: Loan repayment simulation
  Given the loan amount is '10000'
  And the repayment period is '12 months'
  When I send a POST request to '/loan/simulate' with the payload
    | loanAmount | repaymentPeriod |
    | 10000      | 12 months       |
  Then the response status should be 200
  And the response should contain 'loan simulation results'

Scenario: Digital loan application for review and approval
  Given the loan application details are provided
  When I send a POST request to '/loan/apply' with the payload
    | applicationDetails |
    | details            |
  Then the response status should be 200
  And the response should contain 'loan application submitted for review'

Scenario: Viewing active loans and application status
  When I send a GET request to '/loan/status'
  Then the response status should be 200
  And the response should contain 'active loans and application status'

Scenario: Opening a customer service request
  Given the request details are provided
  When I send a POST request to '/support/request' with the payload
    | requestDetails |
    | details        |
  Then the response status should be 200
  And the response should contain 'customer service request opened successfully'

Scenario: Viewing responses and request history
  When I send a GET request to '/support/history'
  Then the response status should be 200
  And the response should contain 'responses and request history'

Scenario: Linking to contact via phone or chat
  When I send a GET request to '/support/contact'
  Then the response status should be 200
  And the response should contain 'contact options available'

Scenario: Checking SSL and encryption usage
  When I send a GET request to '/security/check'
  Then the response status should be 200
  And the response should contain 'communication is encrypted and secure'

Scenario: System availability over time
  When I monitor the system availability
  Then the availability should be at least 99.5%

Scenario: Response time for each action
  When I measure the response time for actions
  Then the response time should be less than 2 seconds

Scenario: Language support for Hebrew and English
  When I check the language support
  Then the system should support Hebrew and English without display or functionality issues
