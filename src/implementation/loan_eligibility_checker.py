# loan_eligibility_checker.py

class LoanEligibilityChecker:
    def __init__(self, monthly_income, credit_score, loan_amount):
        self.monthly_income = monthly_income
        self.credit_score = credit_score
        self.loan_amount = loan_amount

    def is_eligible(self):
        """Check if the user is eligible for a loan."""
        if self.monthly_income < 3000:
            return False, "Monthly income must be at least $3000."
        elif self.credit_score < 500:
            return False, "Credit score must be 500 or higher."
        elif self.loan_amount <= 0:
            return False, "Loan amount must be a positive number."
        elif self.loan_amount > 4 * self.monthly_income:
            return False, "Loan amount cannot exceed 4 times your monthly income."
        else:
            return True, "You are eligible for the loan!"

# Example usage
if __name__ == "__main__":
    monthly_income = float(input("Enter your monthly income: $"))
    credit_score = int(input("Enter your credit score: "))
    loan_amount = float(input("Enter the loan amount requested: $"))

    checker = LoanEligibilityChecker(monthly_income, credit_score, loan_amount)
    eligible, message = checker.is_eligible()
    print(message)

