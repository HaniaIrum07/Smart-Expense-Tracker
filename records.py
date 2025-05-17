# Importing required modules
import database as db
from datetime import datetime, date # For handling and formatting dates

# Class to manage user expenses
class ExpenseManager:
    def __init__(self, user_id):
        self.user_id = user_id  # Store logged-in user's ID

    # Update user's income after any change in expenses
    def update_income_after_expense_change(self):
        # Get original income
        user = db.get_records("User", "UserID = ?", (self.user_id,))
        if not user:
            print("[ERROR] User not found.")
            return

        original_income = user[0][4]  # OriginalIncome column
        expenses = db.get_records("Expenses", "UserID = ?", (self.user_id,))
        total_expense = sum(exp[2] for exp in expenses)
        updated_income = original_income - total_expense

        # Update the current income after expenses are recalculated
        db.update_record("User", {"Income": updated_income}, "UserID = ?", (self.user_id,))

    # Add a new expense entry
    def add_expense(self):
        print("\n=== Add a New Expense ===")
        category = input("Category (e.g., Food, Rent, Travel): ").strip()

        # Validate amount input
        try:
            amount = float(input("Amount: "))
        except ValueError:
            print("[ERROR] Invalid amount.")
            return

        # Allow user to specify a date or use today's date
        input_date = input("Date (YYYY-MM-DD, leave blank for today): ").strip()
        if not input_date:
            expense_date = date.today().isoformat()
        else:
            try:
                datetime.strptime(input_date, "%Y-%m-%d")
                expense_date = input_date
            except ValueError:
                print("[ERROR] Invalid date format.")
                return

        # Fetch user record to get current income for the snapshot
        user = db.get_records("User", "UserID = ?", (self.user_id,))
        if not user:
            print("[ERROR] User not found.")
            return

        income = user[0][3]  # Current Income

        # Construct expense record
        expense_data = {
            "UserID": self.user_id,
            "Amount": amount,
            "Category": category,
            "Date": expense_date,
            "Income": income  #Needed to satisfy NOT NULL
        }

        # Insert into database and update income
        db.insert_record("Expenses", expense_data)
        self.update_income_after_expense_change()
        print("[SUCCESS] Expense added!")

    # View all expenses grouped by category
    def view_expenses(self):
        print("\n=== Your Expenses Grouped by Category ===")
        expenses = db.get_records("Expenses", "UserID = ?", (self.user_id,))
        if not expenses:
            print("No expenses found.")
            return
        # Show updated income
        user = db.get_records("User", "UserID = ?", (self.user_id,))
        current_income = user[0][3] if user else 0
        print(f"\n[INFO] Your current income after expenses: ₹{current_income:.2f}\n")

        # Group expenses by category
        categories = {}
        for exp in expenses:
            category = exp[3]
            if category not in categories:
                categories[category] = []
            categories[category].append(exp)

        # Display expenses per category
        for category, exp_list in categories.items():
            print(f"Category: {category}")
            total = 0
            for exp in exp_list:
                print(f"  ID: {exp[0]} | Amount: {exp[2]}rs | Date: {exp[4]}")
                total += exp[2]
            print(f"  Total in {category}: {total:.2f}rs\n")

    # Edit an existing expense
    def edit_expense(self):
        self.view_expenses()
        expense_id = input("Enter ID to edit: ").strip()

        # Ensure the expense exists and belongs to the user
        exp = db.get_records("Expenses", "ExpenseID = ? AND UserID = ?", (expense_id, self.user_id))
        if not exp:
            print("[ERROR] Expense not found or not yours.")
            return

        print("\nEnter new values (leave blank to keep current):")
        new_amount = input("New Amount: ").strip()
        new_category = input("New Category: ").strip()
        new_date = input("New Date (YYYY-MM-DD): ").strip()

        # Collect fields to update
        updates = {}
        if new_amount:
            try:
                updates["Amount"] = float(new_amount)
            except ValueError:
                print("[ERROR] Invalid amount.")
                return
        if new_category:
            updates["Category"] = new_category
        if new_date:
            try:
                datetime.strptime(new_date, "%Y-%m-%d")
                updates["Date"] = new_date
            except ValueError:
                print("[ERROR] Invalid date format.")
                return

        # If any valid updates provided, update the record
        if updates:
            db.update_record("Expenses", updates, "ExpenseID = ?", (expense_id,))
            self.update_income_after_expense_change()
            print("[SUCCESS] Expense updated.")
        else:
            print("[INFO] No changes made.")

    # Delete an expense
    def delete_expense(self):
        self.view_expenses()
        expense_id = input("Enter ID to delete: ").strip()

        # Check that the expense belongs to the user
        exp = db.get_records("Expenses", "ExpenseID = ? AND UserID = ?", (expense_id, self.user_id))
        if not exp:
            print("[ERROR] Expense not found or not yours.")
            return

        # Confirm deletion
        confirm = input("Are you sure you want to delete this expense? (y/n): ").strip().lower()
        if confirm == 'y':
            db.delete_record("Expenses", "ExpenseID = ?", (expense_id,))
            self.update_income_after_expense_change()
            print("[SUCCESS] Expense deleted.")
        else:
            print("[INFO] Deletion canceled.")

    # Expense menu interface
    def expense_menu(self):
        while True:
            print("\n=== Expense Menu ===")
            print("1. Add Expense")
            print("2. View Expenses")
            print("3. Edit Expense")
            print("4. Delete Expense")
            print("0. Back to Dashboard")

            choice = input("Choose an option: ").strip()
            if choice == "1":
                self.add_expense()
            elif choice == "2":
                self.view_expenses()
            elif choice == "3":
                self.edit_expense()
            elif choice == "4":
                self.delete_expense()
            elif choice == "0":
                break
            else:
                print("[ERROR] Invalid choice.")
