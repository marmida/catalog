Feature: backend API

Scenario: retrieve tag list
When I request the list of tags
Then the response should contain "Pretentious bullshit"
And "Aliens" should come before "Pretentious bullshit"
