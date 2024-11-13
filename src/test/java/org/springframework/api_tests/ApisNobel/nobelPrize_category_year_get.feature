# ********RoostGPT********

# Test generated by RoostGPT for test api-spec using AI Type  and AI Model 
# 
# Feature file generated for /nobelPrize/{category}/{year}_get for http method type GET 
# RoostTestHash=adfce3f1d2
# 
# 

# ********RoostGPT********
Feature: Nobel Prize API Tests

  Background:
    * def urlBase = karate.properties['url.base'] || karate.get('urlBase', 'http://localhost:4010')
    * url urlBase
    * configure headers = { Authorization: '#(karate.properties["AUTH_TOKEN"])' }

  Scenario Outline: Verify Nobel Prize details with valid category and year
    Given path '/2.1/nobelPrize/<category>/<year>'
    When method GET
    Then status 200
    And match response.nobelPrize.awardYear == '#number'
    And match response.nobelPrize.category.en == '#string'
    And match response.nobelPrize.categoryFullName.en == '#string'
    And match response.nobelPrize.dateAwarded == '#string'
    And match response.nobelPrize.prizeAmount == '#number'
    And match response.nobelPrize.prizeAmountAdjusted == '#number'
    And match response.nobelPrize.topMotivation.en == '#string'
    And match response.nobelPrize.laureates == '#array'
    And match response.nobelPrize.laureates[*].id == '#number'
    And match response.nobelPrize.laureates[*].name.en == '#string'
    And match response.nobelPrize.laureates[*].portion == '#string'
    And match response.nobelPrize.laureates[*].sortOrder == '#string'
    And match response.nobelPrize.laureates[*].motivation.en == '#string'
    And match response.nobelPrize.laureates[*].links == '#array'
    And match response.nobelPrize.laureates[*].links[*].rel == '#string'
    And match response.nobelPrize.laureates[*].links[*].href == '#string'
    And match response.nobelPrize.laureates[*].links[*].action == '#string'
    And match response.nobelPrize.laureates[*].links[*].types == '#string'

    Examples:
      | read('nobelPrize_category_year_get.csv') |

  Scenario Outline: Verify handling of invalid category or year
    Given path '/2.1/nobelPrize/<category>/<year>'
    When method GET
    Then status <status>
    And match response.code == '#string'
    And match response.message == '#string'

    Examples:
      | category | year | status |
      | abc      | 2020 |    404 |
      | che      | 1899 |    422 |
      | med      | 3000 |    400 |
