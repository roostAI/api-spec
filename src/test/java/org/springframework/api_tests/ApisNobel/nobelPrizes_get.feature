# ********RoostGPT********

# Test generated by RoostGPT for test api-spec using AI Type  and AI Model 
# 
# Feature file generated for /nobelPrizes_get for http method type GET 
# RoostTestHash=4940f5c55b
# 
# 

# ********RoostGPT********
Feature: Test Nobel Prizes API

  Background:
    * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:4010')
    * url urlBase
    * configure headers = { Authorization: '#(karate.properties["AUTH_TOKEN"])' }

  Scenario Outline: Test GET /2.1/nobelPrizes with valid query parameters
    Given path '2.1/nobelPrizes'
    And param offset = <offset>
    And param limit = <limit>
    And param sort = '<sort>'
    And param nobelPrizeYear = <nobelPrizeYear>
    And param yearTo = <yearTo>
    And param nobelPrizeCategory = '<nobelPrizeCategory>'
    And param format = '<format>'
    And param csvLang = '<csvLang>'
    When method GET
    Then status 200
    And match response.nobelPrizes == '#[]'
    And match response.meta.offset == <offset>
    And match response.meta.limit == <limit>
    And match response.meta.nobelPrizeYear == <nobelPrizeYear>
    And match response.meta.yearTo == <yearTo>
    And match response.meta.nobelPrizeCategory == '<nobelPrizeCategory>'
    And match response.meta.count == '#number'
    And match response.links == '#[]'

    Examples:
      | read('nobelPrizes_get.csv') |

  Scenario: Test GET /2.1/nobelPrizes with invalid query parameters
    Given path '2.1/nobelPrizes'
    And param offset = -1
    And param limit = 0
    And param nobelPrizeYear = 1800
    When method GET
    Then status 400
    And match response.code == '400'
    And match response.message == '#string'

  Scenario: Test GET /2.1/nobelPrizes with non-existing endpoint
    Given path '2.1/nobelPrizesNonExistent'
    When method GET
    Then status 404
    And match response.code == '404'
    And match response.message == '#string'

  Scenario: Test GET /2.1/nobelPrizes with semantic errors
    Given path '2.1/nobelPrizes'
    And param nobelPrizeYear = 2020
    And param yearTo = 2019
    When method GET
    Then status 422
    And match response.code == '422'
    And match response.message == '#string'
