import pandas as pd
import numpy as np

# Function to load the dataset
def load_data():
    df = pd.read_csv('synthetic_expense_data.csv')
    return df

# Function to preprocess the data
def preprocess_data(df):
    # Define which columns represent expense categories
    expense_cols = ['Food', 'Transport', 'Entertainment', 'Housing', 'Others']

    # Compute Total_Expenses and Savings for consistency (even if already in the CSV)
    df['Total_Expenses'] = df[expense_cols].sum(axis=1)
    df['Savings'] = df['Income'] - df['Total_Expenses']

    # Prepare feature matrix (X) and target vector (y)
    X = df[expense_cols].values
    y = df['Savings'].values.reshape(-1, 1)

    # Add intercept (bias) term to X
    X_b = np.hstack([np.ones((X.shape[0], 1)), X])
    return X_b, y, expense_cols

# Function to split the data into training and testing sets (80/20 split)
def split_data(X_b, y):
    split_index = int(len(X_b) * 0.8)
    return X_b[:split_index], X_b[split_index:], y[:split_index], y[split_index:]

# Train a linear regression model using the normal equation
def train_model(X_train, y_train):
    theta = np.linalg.inv(X_train.T @ X_train) @ X_train.T @ y_train
    return theta

# Make predictions using theta
def make_predictions(X, theta):
    return X @ theta

# Evaluate the model using Mean Squared Error
def evaluate_model(y_pred, y_test):
    mse = np.mean((y_pred - y_test) ** 2)
    print(f" Lightweight Training Done | Test MSE: {mse:.2f}")

# Main training pipeline to return model parameters (theta) and column labels
def train_and_return_theta():
    df = load_data()
    X_b, y, expense_cols = preprocess_data(df)
    X_train, X_test, y_train, y_test = split_data(X_b, y)
    theta = train_model(X_train, y_train)
    y_pred = make_predictions(X_test, theta)
    evaluate_model(y_pred, y_test)
    return theta, expense_cols

# Function to predict savings given new user expense data
def predict_savings(user_expenses, theta, expense_cols):
    # Create a DataFrame for consistent ordering
    df = pd.DataFrame([user_expenses], columns=expense_cols)

    # Add bias (intercept) term
    X = np.hstack([np.ones((df.shape[0], 1)), df.values])

    # Predict savings
    predicted = X @ theta

    # Return scalar float value safely
    return float(predicted[0])