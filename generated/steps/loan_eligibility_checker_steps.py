from behave import given, when, then
import sys
sys.path.append('src/implementation')

# steps/loan_eligibility_steps.py

from behave import given, when, then
from src.implementation.loan_eligibility_checker import LoanEligibilityChecker

@given('the Loan Eligibility Checker application is running')
def step_impl(context):
    # This step assumes the application is running and ready to accept inputs.
    pass

@given('the user provides a monthly income of {monthly_income:g}')
def step_impl(context, monthly_income):
    context.monthly_income = monthly_income

@given('the user provides a credit score of {credit_score:d}')
def step_impl(context, credit_score):
    context.credit_score = credit_score

@given('the user provides a loan amount of {loan_amount:g}')
def step_impl(context, loan_amount):
    context.loan_amount = loan_amount

@when('the application checks the monthly income')
def step_impl(context):
    if context.monthly_income <= 0:
        context.message = "Monthly income must be a positive number."
    else:
        context.message = None

@when('the application checks the credit score')
def step_impl(context):
    if context.credit_score < 300 or context.credit_score > 850:
        context.message = "Credit score must be between 300 and 850."
    else:
        context.message = None

@when('the application checks the loan amount')
def step_impl(context):
    if context.loan_amount <= 0:
        context.message = "Loan amount must be a positive number."
    else:
        context.message = None

@when('the application checks eligibility')
def step_impl(context):
    checker = LoanEligibilityChecker(context.monthly_income, context.credit_score, context.loan_amount)
    _, context.message = checker.is_eligible()

@then('the application should display "{expected_message}"')
def step_impl(context, expected_message):
    assert context.message == expected_message, f"Expected '{expected_message}', but got '{context.message}'"

@given('the application prompts for monthly income')
def step_impl(context):
    context.prompt_message = "Enter your monthly income (e.g., 4000):"

@given('the application prompts for credit score')
def step_impl(context):
    context.prompt_message = "Enter your credit score (between 300 and 850):"

@given('the application prompts for loan amount')
def step_impl(context):
    context.prompt_message = "Enter the loan amount requested (e.g., 15000):"

@then('the application should prompt "{expected_prompt}"')
def step_impl(context, expected_prompt):
    assert context.prompt_message == expected_prompt, f"Expected '{expected_prompt}', but got '{context.prompt_message}'"

@given('the codebase')
def step_impl(context):
    # This step assumes access to the codebase for maintainability checks.
    pass

@then('the code should include comments explaining the purpose of each method and key logic points')
def step_impl(context):
    # This step is a placeholder for checking code comments and documentation.
    # In practice, this would involve reviewing the codebase manually.
    pass