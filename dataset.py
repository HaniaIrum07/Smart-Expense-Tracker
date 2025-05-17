import pandas as pd
import random
from datetime import datetime, timedelta

# Configuration
num_users = 20
num_months = 12
categories = ['Food', 'Transport', 'Entertainment', 'Housing', 'Others']
records = []

user_ids = [f"user_{i+1}" for i in range(num_users)]
start_date = datetime(2023, 1, 1)

for user in user_ids:
    for month_offset in range(num_months):
        date = start_date + timedelta(days=30 * month_offset)
        income = random.randint(3000, 7000)
        for category in categories:
            amount = round(random.uniform(50, 900), 2)
            records.append({
                "UserID": user,
                "Amount": amount,
                "Category": category,
                "Date": date.strftime('%Y-%m-%d'),
                "Income": income
            })

# Create DataFrame
df = pd.DataFrame(records)

# Pivot into feature matrix
df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')
pivot_df = df.pivot_table(index=['UserID', 'Month', 'Income'],
                          columns='Category',
                          values='Amount',
                          aggfunc='sum',
                          fill_value=0).reset_index()

pivot_df['Total_Expenses'] = pivot_df[categories].sum(axis=1)
pivot_df['Savings'] = pivot_df['Income'] - pivot_df['Total_Expenses']

# Save to CSV
pivot_df.to_csv("synthetic_expense_data.csv", index=False)
print("Dataset saved as 'synthetic_expense_data.csv'")

print(pd.read_csv("synthetic_expense_data.csv").columns)
