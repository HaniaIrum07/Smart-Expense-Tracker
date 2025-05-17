# Import necessary libraries
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# Function to generate monthly graphical analysis for a user
def generate_graphs(user_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('budget_management.db')
    cursor = conn.cursor()

    # Define the date range: from the 1st to today's date of the current month
    today = datetime.today()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = today

    # === Fetch Expenses Grouped by Category ===
    cursor.execute('''
        SELECT Category, SUM(Amount)
        FROM Expenses
        WHERE UserID = ? AND Date BETWEEN ? AND ?
        GROUP BY Category
    ''', (user_id, first_day_of_month.date(), last_day_of_month.date()))
    expenses = cursor.fetchall()

    # === Fetch Transactions Grouped by Type ===
    cursor.execute('''
        SELECT TransactionType, SUM(Amount)
        FROM Transactions
        WHERE UserID = ? AND Date BETWEEN ? AND ?
        GROUP BY TransactionType
    ''', (user_id, first_day_of_month.date(), last_day_of_month.date()))
    transactions = cursor.fetchall()

    # If no data is available, notify user and exit
    if not expenses and not transactions:
        print("[INFO] No data available for the current month.")
        return

    # Prepare subplots (1 row, 2 columns)
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    # Pie chart for expenses
    if expenses:
        axs[0].pie(
            [item[1] for item in expenses],
            labels=[item[0] for item in expenses],
            autopct='%1.1f%%',
            startangle=90
        )
        axs[0].set_title('Expense Distribution by Category (This Month)')
        axs[0].axis('equal')  # Keep aspect ratio equal for a circular pie

    else:
        # Show placeholder if no expense data
        axs[0].text(0.5, 0.5, 'No Expenses Found', ha='center', va='center', fontsize=12)
        axs[0].set_title('Expense Distribution')

    # === Plot Transactions as a Bar Chart ===
    if transactions:
        axs[1].bar(
            [item[0] for item in transactions],
            [item[1] for item in transactions],
            color=['orange', 'green']   # Bar colors
        )
        axs[1].set_title('Transaction Summary (This Month)')
        axs[1].set_xlabel('Transaction Type')
        axs[1].set_ylabel('Amount')

    else:
        # Show placeholder if no transaction data
        axs[1].text(0.5, 0.5, 'No Transactions Found', ha='center', va='center', fontsize=12)
        axs[1].set_title('Transaction Summary')

    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.show()

    # Close the database connection
    conn.close()
