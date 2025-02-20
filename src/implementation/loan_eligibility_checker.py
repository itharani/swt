class LoanEligibilityChecker:
    def __init__(self, monthly_income, credit_score, loan_amount):
        self.monthly_income = monthly_income
        self.credit_score = credit_score
        self.loan_amount = loan_amount

    def is_eligible(self):
        """Check if the user is eligible for a loan."""
        reasons = []
        
        if self.monthly_income <= 0:
            return False, "Monthly income must be a positive number."
        if self.credit_score < 300 or self.credit_score > 950:
            return False, "Credit score must be an integer between 300 and 850."
        if self.loan_amount <= 0:
            return False, "Loan amount must be a positive number."

        if self.monthly_income < 3000:
            reasons.append("Monthly income must be at least $3000.")
        if self.credit_score < 500:
            reasons.append("Credit score must be 500 or higher.")
        if self.loan_amount > 4 * self.monthly_income:
            reasons.append("Loan amount cannot exceed 4 times your monthly income.")

        if reasons:
            return False, "You are not eligible for the loan. Reasons: " + "; ".join(reasons)
        
        return True, "You are eligible for the loan! Proceed with your application."

# Example usage
if __name__ == "__main__":
    try:
        monthly_income = float(input("Enter your monthly income: $"))
        credit_score = int(input("Enter your credit score: "))
        loan_amount = float(input("Enter the loan amount requested: $"))
        
        checker = LoanEligibilityChecker(monthly_income, credit_score, loan_amount)
        eligible, message = checker.is_eligible()
        print(message)
    except ValueError:
        print("Invalid input. Please enter numeric values for income and loan amount, and an integer for credit score.")
