# Business Requirement Document (BRD)

## Project Name: Loan Eligibility Checker  
**Version:** 1.0  
**Author:** Your Name  
**Date:** [Today's Date]  

---

## 1. Introduction  
The Loan Eligibility Checker is a Python application that determines whether a user is eligible for a loan based on their monthly income, credit score, and loan amount requested.

## 2. Business Requirements  
The application must meet the following requirements:

### Input Requirements  
The user must provide:
- Monthly income (in dollars).
- Credit score (an integer between 300 and 850).
- Loan amount requested (in dollars).

### Eligibility Rules  
The user is eligible for a loan if:
- Their monthly income is at least $3000.
- Their credit score is 500 or higher.
- The loan amount requested does not exceed 4 times their monthly income.

### Output Requirements  
The application must display:
- A message indicating whether the user is eligible for the loan followed by an appropriate call to action.
- If the user is not eligible, the reason(s) for ineligibility.

## 3. Functional Requirements  

### Input Validation  
The application must validate user input to ensure:
- Monthly income is a positive number.
- Credit score is an integer between 300 and 850.
- Loan amount is a positive number.

### Eligibility Check  
The application must implement the eligibility rules as described in Section 2.

### Output Display  
The application must display the eligibility result and any relevant messages to the user.