Feature: API Testing for Banking Application

Background:
  Given the API base URL 'http://api.bankofjerusalem.com'
  And the authorization header is set
  And the content type is 'application/json'

Scenario: User Login with Identity Number and OTP
  Given the user has a registered account and a mobile number
  When I send a POST request to '/login' with payload
    | identityNumber | '123456789' |
    | otp            | '123456'    |
  Then the response status should be 200
  And the response should contain 'User is successfully logged in'
  And the user is redirected to the account dashboard

Scenario: Biometric Login
  Given the user device supports biometric authentication and it is set up
  When I send a POST request to '/biometric-login' with payload
    | biometricData | 'fingerprintData' |
  Then the response status should be 200
  And the response should contain 'User is successfully logged in'
  And the user is redirected to the account dashboard

Scenario: Account Balance Viewing
  Given the user is logged in
  When I send a GET request to '/account/balance'
  Then the response status should be 200
  And the response should contain 'The account balance is displayed correctly'

Scenario: Transaction History Filtering
  Given the user is logged in
  When I send a GET request to '/transaction-history' with parameters
    | dateRange       | '2023-01-01 to 2023-01-31' |
    | transactionType | 'credit'                    |
  Then the response status should be 200
  And the response should contain 'Filtered transactions are displayed according to the selected criteria'

Scenario: Internal Fund Transfer
  Given the user is logged in and has sufficient balance
  When I send a POST request to '/transfer/internal' with payload
    | recipientAccount | '987654321' |
    | amount           | '1000'      |
  Then the response status should be 200
  And the response should contain 'Funds are transferred successfully'
  And a confirmation message is displayed

Scenario: Adding a New Beneficiary
  Given the user is logged in
  When I send a POST request to '/beneficiaries' with payload
    | beneficiaryName | 'John Doe' |
    | accountNumber   | '1234567890' |
    | smsCode         | '654321'      |
  Then the response status should be 200
  And the response should contain 'New beneficiary is added successfully'

Scenario: Loan Request Simulation
  Given the user is logged in
  When I send a POST request to '/loan/simulate' with payload
    | loanAmount      | '50000'       |
    | repaymentTerms  | '24 months'   |
  Then the response status should be 200
  And the response should contain 'Monthly repayment amount is calculated and displayed'

Scenario: System Security
  When a security audit is performed
  Then the response should confirm 'All user data is secured with SSL and encryption methods'

Scenario: System Availability
  When the system uptime is monitored over a period
  Then the response should confirm 'System availability is at least 99.5%'

Scenario: Performance Testing
  When load testing is performed with multiple users
  Then the response should confirm 'All actions are completed within 2 seconds'
