from Register import UserRegistration  # Import the UserRegistration class
from login import UserLogin  # Import the UserLogin class
from dashboard import dashboard  # Import the dashboard function
import analysis  # Import the analysis module for generating graphs
from training import train_and_return_theta, predict_savings #for prediction1

def main():
    while True:
        print("\n=== Welcome to Expense Tracker ===")
        print("1. Register")
        print("2. Login")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            # User registration process
            registration = UserRegistration()
            user_data = registration.register_user()
            print("[SUCCESS] Registration completed successfully.")

        elif choice == "2":
            # User login process
            login = UserLogin()
            user_id = login.login_user()

            if user_id:  # Only if login is successful
                print(f"[SUCCESS] Welcome, {user_id}!")
                dashboard(user_id)  # Open the dashboard for the logged-in user
            else:
                print("[ERROR] Login failed. Please try again.")

        elif choice == "0":
            # Exit the program
            print("Goodbye!")
            break

        else:
            # Handle invalid input
            print("[ERROR] Invalid choice. Please try again.")

# Ensure the script runs only when executed directly, not when imported
if __name__ == "__main__":
    main()