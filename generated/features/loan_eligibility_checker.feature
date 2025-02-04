Feature: Loan Eligibility Checker

  # This feature file consolidates all business requirements for the Loan Eligibility Checker application.
  # It includes scenarios to test input validation, eligibility rules, and output display.

  Background:
    Given the Loan Eligibility Checker application is running

  Scenario: Validate user input
    Given the user provides a monthly income of -1000
    When the application checks the monthly income
    Then the application should display "Monthly income must be a positive number."

    Given the user provides a credit score of 250
    When the application checks the credit score
    Then the application should display "Credit score must be between 300 and 850."

    Given the user provides a loan amount of -5000
    When the application checks the loan amount
    Then the application should display "Loan amount must be a positive number."

  Scenario: Check loan eligibility
    Given the user provides a monthly income of 4000
    And the user provides a credit score of 600
    And the user provides a loan amount of 15000
    When the application checks eligibility
    Then the application should display "You are eligible for the loan!"

    Given the user provides a monthly income of 2500
    And the user provides a credit score of 600
    And the user provides a loan amount of 10000
    When the application checks eligibility
    Then the application should display "Monthly income must be at least $3000."

    Given the user provides a monthly income of 4000
    And the user provides a credit score of 400
    And the user provides a loan amount of 15000
    When the application checks eligibility
    Then the application should display "Credit score must be 500 or higher."

    Given the user provides a monthly income of 4000
    And the user provides a credit score of 600
    And the user provides a loan amount of 20000
    When the application checks eligibility
    Then the application should display "Loan amount cannot exceed 4 times your monthly income."

  Scenario: Display eligibility result
    Given the user provides a monthly income of 4000
    And the user provides a credit score of 600
    And the user provides a loan amount of 15000
    When the application checks eligibility
    Then the application should display "You are eligible for the loan!"

    Given the user provides a monthly income of 2500
    And the user provides a credit score of 600
    And the user provides a loan amount of 10000
    When the application checks eligibility
    Then the application should display "Monthly income must be at least $3000."

  Scenario: Usability improvements
    Given the application prompts for monthly income
    Then the application should prompt "Enter your monthly income (e.g., 4000):"

    Given the application prompts for credit score
    Then the application should prompt "Enter your credit score (between 300 and 850):"

    Given the application prompts for loan amount
    Then the application should prompt "Enter the loan amount requested (e.g., 15000):"

  Scenario: Maintainability improvements
    Given the codebase
    Then the code should include comments explaining the purpose of each method and key logic points