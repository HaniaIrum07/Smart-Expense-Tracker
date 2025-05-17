# Import required modules
import database as db
from datetime import datetime


class TransactionManager:
    def __init__(self, user_id):
        self.user_id = user_id  # Store user_id for use in methods

    # === Method to Add a New Transaction ===
    def add_transaction(self):
        print("\n=== Add a New Transaction ===")

        # Get transaction type (sent or received)
        while True:
            transaction_type = input("Transaction Type (sent/received): ").lower()
            if transaction_type in ["sent", "received"]:
                break
            else:
                print("[ERROR] Invalid transaction type. Please enter 'sent' or 'received'.")

        # Prompt for transaction amount
        try:
            amount = float(input("Amount: "))
        except ValueError:
            print("[ERROR] Invalid amount.")
            return

        # Prompt for transaction date or default to today's date
        date = input("Date (YYYY-MM-DD, leave blank for today): ")
        if not date:
            date = datetime.today().strftime('%Y-%m-%d')

        # Prepare transaction record
        transaction_data = {
            "UserID": self.user_id,
            "TransactionType": transaction_type,
            "Amount": amount,
            "Date": date
        }

        # Update the user's income based on the transaction type
        self._update_income(transaction_type, amount)

        # Insert the transaction into the Transactions table
        db.insert_record("Transactions", transaction_data)
        print("[SUCCESS] Transaction added!")

    # === Private Method to Update User's Income ===
    def _update_income(self, transaction_type, amount):
        """
        Update the user's income based on the transaction type.
        If the transaction is 'sent', subtract the amount.
        If the transaction is 'received', add the amount.
        """
        # Fetch current income
        user_record = db.get_records("User", "UserID = ?", (self.user_id,))
        if not user_record:
            print("[ERROR] User not found.")
            return

        current_income = user_record[0][3]  # Income is at index 3 in the User table

        if transaction_type == "sent":
            new_income = current_income - amount  # Subtract for sent transactions
        elif transaction_type == "received":
            new_income = current_income + amount  # Add for received transactions

        # Update the income in the User table
        db.update_record("User", {"Income": new_income}, "UserID = ?", (self.user_id,))
        print(f"[SUCCESS] User's income updated to {new_income}.")

    # === Method to View All Transactions ===
    def view_transactions(self):
        print("\n=== Your Transactions ===")

        # Fetch the transactions for the user
        transactions = db.get_records("Transactions", "UserID = ?", (self.user_id,))
        if not transactions:
            print("No transactions found.")
            return

        # Fetch the current income for the user
        user_record = db.get_records("User", "UserID = ?", (self.user_id,))
        if not user_record:
            print("[ERROR] User not found.")
            return

        current_income = user_record[0][3]  # Income is at index 3 in the User table

        # Display current income along with transactions
        print(f"Current Income: {current_income}")

        for i, txn in enumerate(transactions, 1):
            print(f"\nTransaction {i}")
            print(f"ID            : {txn[0]}")
            print(f"Type          : {txn[2]}")
            print(f"Amount        : {txn[3]}")
            print(f"Date          : {txn[4]}")

    # === Transaction Menu Loop ===
    def transaction_menu(self):
        while True:
            print("\n=== Transaction Menu ===")
            print("1. Add Transaction")
            print("2. View Transactions")
            print("0. Back to Dashboard")

            # Menu option handling
            choice = input("Choose an option: ")
            if choice == "1":
                self.add_transaction()
            elif choice == "2":
                self.view_transactions()
            elif choice == "0":
                break
            else:
                print("[ERROR] Invalid choice.")


# === Entry Point for Direct Script Execution ===
if __name__ == "__main__":
    # Prompt for User ID and validate it
    while True:
        user_id = input("Enter User ID to test: ")  # For testing purposes, you can replace this with a valid user_id

        # Check if the User ID exists in the database
        user_record = db.get_records("User", "UserID = ?", (user_id,))
        if not user_record:
            print("[ERROR] User ID does not exist in the database. Please enter a valid User ID.")
        else:
            # If the user exists, proceed with Transaction Management
            transaction_manager = TransactionManager(user_id)

            # Show transaction menu
            transaction_manager.transaction_menu()

            # Exit after successful execution
            break


