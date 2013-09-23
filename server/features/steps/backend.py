from behave import when, then
import requests

@when('I request the list of tags')
def step_impl(context):
    context.response = requests.get(context._url() + '/tags')

@then('the response should contain "{tag}"')
def step_impl(context, tag):
    assert tag in context.response.json()

@then('"{tag1}" should come before "{tag2}"')
def step_imply(context, tag1, tag2):
    r = context.response.json()
    assert r.index(tag1) < r.index(tag2)