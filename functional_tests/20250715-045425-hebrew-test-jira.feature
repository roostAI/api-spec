Feature: בדיקת API לאפליקציית מובייל בנק ירושלים

Background:
  Given the API base URL 'https://api.bankjerusalem.co.il'
  And the authorization header is set
  And the content type is 'application/json'

Scenario: כניסה לאפליקציה עם מספר זהות וקוד סודי
  Given the user is registered and his phone is connected to the network
  When I send a POST request to '/login' with the payload:
    | id_number | secret_code |
    | 123456789 | 987654      |
  Then the response status should be 200
  And the response should contain 'home screen details'

Scenario: זיהוי ביומטרי לכניסה לאפליקציה
  Given the user has set up biometric identification on his device and the app supports it
  When I send a POST request to '/biometric-login' with the payload:
    | biometric_data |
    | valid_fingerprint_or_faceid |
  Then the response status should be 200
  And the response should indicate successful login

Scenario: נעילת חשבון לאחר 3 ניסיונות כושלים
  Given the user is registered in the system
  When I send a POST request to '/login' with incorrect credentials three times
    | id_number | secret_code |
    | 123456789 | wrong_code  |
  Then the response status should be 403
  And the response should contain 'account locked message'

Scenario: צפייה בפרטי חשבון
  Given the user is logged into the application
  When I send a GET request to '/account-details'
  Then the response status should be 200
  And the response should contain 'general balances and transactions'

Scenario: בדיקת ביצועים וזמני תגובה
  Given the application is installed and connected to a stable network
  When I perform various actions like viewing account details and transferring funds
  Then each action response time should not exceed 2 seconds
