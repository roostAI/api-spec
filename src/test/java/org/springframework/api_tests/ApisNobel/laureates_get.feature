# ********RoostGPT********

# Test generated by RoostGPT for test api-spec using AI Type  and AI Model 
# 
# Feature file generated for /laureates_get for http method type GET 
# RoostTestHash=bb9ad621b1
# 
# 

# ********RoostGPT********
Feature: Nobel Laureates API

  Background:
    * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:4010')
    * url urlBase

  Scenario: Get all laureates with default parameters
    Given path '/2.1/laureates'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    When method GET
    Then status 200
    And match response.laureates == '#array'
    And match response.meta == '#object'
    And match response.links == '#array'

  Scenario Outline: Get laureates with query parameters
    Given path '/2.1/laureates'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param offset = <offset>
    And param limit = <limit>
    And param sort = '<sort>'
    When method GET
    Then status 200
    And match response.laureates == '#array'
    And match response.meta.offset == <offset>
    And match response.meta.limit == <limit>
    And match response.meta.sort == '<sort>'

    Examples:
      | read('laureates_get.csv') |

  Scenario: Search laureates by name
    Given path '/2.1/laureates'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param name = 'Marie Curie'
    When method GET
    Then status 200
    And match response.laureates[*].laureateIfPerson.knownName.en contains 'Marie Curie'

  Scenario: Search laureates by gender
    Given path '/2.1/laureates'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param gender = 'female'
    When method GET
    Then status 200
    And match each response.laureates[*].laureateIfPerson.gender == 'female'

  Scenario: Search laureates by Nobel Prize category
    Given path '/2.1/laureates'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param nobelPrizeCategory = 'phy'
    When method GET
    Then status 200
    And match response.laureates[*].nobelPrizes[*].category.en contains 'Physics'

  Scenario: Search laureates by birth date range
    Given path '/2.1/laureates'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param birthDate = '1900'
    And param birthDateTo = '1950'
    When method GET
    Then status 200
    And match each response.laureates[*].laureateIfPerson.birth.date == '#regex \\d{4}-\\d{2}-\\d{2}'
    And match each response.laureates[*].laureateIfPerson.birth.date >= '1900-01-01'
    And match each response.laureates[*].laureateIfPerson.birth.date <= '1950-12-31'

  Scenario: Get laureate by ID
    Given path '/2.1/laureates'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param ID = 1
    When method GET
    Then status 200
    And match response.laureates[0].id == 1

  Scenario: Invalid request - non-existent laureate ID
    Given path '/2.1/laureates'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param ID = 999999
    When method GET
    Then status 404
    And match response.code == '404'
    And match response.message == '#string'

  Scenario: Invalid request - incorrect parameter type
    Given path '/2.1/laureates'
    And header Authorization = 'Bearer ' + karate.properties['AUTH_TOKEN']
    And param limit = 'invalid'
    When method GET
    Then status 400
    And match response.code == '400'
    And match response.message == '#string'
