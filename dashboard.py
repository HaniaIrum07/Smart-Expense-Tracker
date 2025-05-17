import database as db
from records import ExpenseManager
from transactions import TransactionManager
import analysis

# Import model training and prediction functions
from training import train_and_return_theta, predict_savings


# ======================= Dashboard Entry ========================
def dashboard(user_id):
    # Load the linear regression model (weights) and expense columns once at dashboard entry
    theta, expense_cols = train_and_return_theta()

    while True:
        print("\n=== User Dashboard ===")

        # Fetch current user's record from the database
        user_record = db.get_records("User", "UserID = ?", (user_id,))
        if not user_record:
            print("[ERROR] User not found.")
            return

        user = user_record[0]

        # Display user info and dashboard options
        print(f"\nYour current details:\n")
        print(f"1. User ID         : {user[0]}")
        print(f"2. Email           : {user[1]}")
        print(f"3. Password        : {user[2]}")
        print(f"4. Original Income : {user[4]}")
        print("5. Manage Expenses")
        print("6. Manage Transactions")
        print("7. View Graphical Analysis")
        print("8. Predict Your Savings")
        print("0. Exit Dashboard")

        choice = input("\nEnter your choice (0 to exit): ")

        if choice == "0":
            print("Exiting dashboard...")
            break

        # ================= Update User ID =================
        elif choice == "1":
            new_user_id = input("Enter new User ID (alphanumeric): ")
            if not new_user_id.isalnum():
                print("[ERROR] User ID must be alphanumeric.")
                continue
            db.update_record("User", {"UserID": new_user_id}, "UserID = ?", (user_id,))
            user_id = new_user_id
            print("[SUCCESS] User ID updated.")

        # ================= Update Email =================
        elif choice == "2":
            new_email = input("Enter new email: ")
            db.update_record("User", {"Email": new_email}, "UserID = ?", (user_id,))
            print("[SUCCESS] Email updated.")

        # ================= Update Password =================
        elif choice == "3":
            new_password = input("Enter new password (8 characters): ")
            if len(new_password) != 8:
                print("[ERROR] Password must be exactly 8 characters.")
                continue
            db.update_record("User", {"Password": new_password}, "UserID = ?", (user_id,))
            print("[SUCCESS] Password updated.")

        # ================= Income Editing Disabled =================
        elif choice == "4":
            print("[INFO] Original income cannot be edited from the dashboard.")

        # ================= Expense Management =================
        elif choice == "5":
            print("[DEBUG] Redirecting to expense menu...")
            expense_manager = ExpenseManager(user_id)
            expense_manager.expense_menu()

        # ================= Transaction Management =================
        elif choice == "6":
            print("[DEBUG] Redirecting to transaction menu...")
            transaction_manager = TransactionManager(user_id)
            transaction_manager.transaction_menu()

        # ================= Graphical Analysis =================
        elif choice == "7":
            print("\n=== Generating Graphical Analysis ===")
            analysis.generate_graphs(user_id)
            print("[INFO] Analysis completed.")

        # ================= AI-Based Savings Prediction =================
        elif choice == "8":
            print("\n=== Predict Your Savings ===")
            print("Enter your estimated monthly expenses:")

            try:
                # Collect user-input expenses for each relevant category
                user_expenses = {}
                for col in expense_cols:
                    amount = float(input(f"{col}: "))
                    user_expenses[col] = amount

                # Run prediction using the model
                predicted = predict_savings(user_expenses, theta, expense_cols)
                print(f"\n💡 Estimated Savings This Month: ${predicted:.2f}")

            except Exception as e:
                print(f"[ERROR] Failed to predict savings: {e}")

        # ================= Invalid Input Handling =================
        else:
            print("[ERROR] Invalid choice. Please try again.")

# ================= Login Simulation for Direct Script Execution =================
if __name__ == "__main__":
    from login import UserLogin

    login = UserLogin()
    user_id = login.login_user()

    if user_id:
        dashboard(user_id)
    else:
        print("[ERROR] Invalid login credentials.")
