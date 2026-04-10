# etl/src/generate_data.py
import pandas as pd
import numpy as np
from faker import Faker
import uuid
from datetime import datetime, timedelta
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

fake = Faker()
Faker.seed(42)
np.random.seed(42)

def generate_customers(num_records=1000):
    counties = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Uasin Gishu']
    statuses = ['Salaried', 'Self-Employed', 'Unemployed']
    
    customers = []
    for _ in range(num_records):
        customers.append({
            'customer_id': str(uuid.uuid4())[:8],
            'age': np.random.randint(18, 65),
            'location_county': np.random.choice(counties, p=[0.4, 0.2, 0.15, 0.15, 0.1]),
            'employment_status': np.random.choice(statuses, p=[0.5, 0.4, 0.1]),
            'monthly_income': round(np.random.uniform(20000, 250000), 2)
        })
    return pd.DataFrame(customers)

def generate_loans(df_customers):
    loans = []
    statuses = ['Active', 'Closed', 'Defaulted']
    
    # 80% of customers get a loan
    borrowers = df_customers.sample(frac=0.8, random_state=42)
    
    for _, customer in borrowers.iterrows():
        # Higher income = potentially larger loan
        max_loan = customer['monthly_income'] * 5 
        
        loans.append({
            'loan_id': str(uuid.uuid4())[:8],
            'customer_id': customer['customer_id'],
            'principal_amount': round(np.random.uniform(5000, max_loan), 2),
            'interest_rate': round(np.random.uniform(10.0, 25.0), 2), # 10% to 25%
            'loan_term_months': np.random.choice([3, 6, 12, 24]),
            'disbursement_date': fake.date_between(start_date='-2y', end_date='today'),
            'status': np.random.choice(statuses, p=[0.6, 0.3, 0.1])
        })
    return pd.DataFrame(loans)

def generate_repayments(df_loans):
    repayments = []
    
    for _, loan in df_loans.iterrows():
        # Active loans have fewer payments, closed have all, defaulted have some
        if loan['status'] == 'Closed':
            num_payments = loan['loan_term_months']
        elif loan['status'] == 'Defaulted':
            num_payments = np.random.randint(1, max(2, loan['loan_term_months'] // 2))
        else: # Active
            num_payments = np.random.randint(1, loan['loan_term_months'])

        monthly_due = (loan['principal_amount'] * (1 + (loan['interest_rate']/100))) / loan['loan_term_months']
        
        start_date = loan['disbursement_date']
        
        for i in range(num_payments):
            payment_date = start_date + timedelta(days=30 * (i + 1))
            # Simulate late payments (higher chance for defaulted loans)
            is_late_prob = 0.8 if loan['status'] == 'Defaulted' else 0.1
            is_late = np.random.choice([True, False], p=[is_late_prob, 1 - is_late_prob])
            
            repayments.append({
                'repayment_id': str(uuid.uuid4())[:8],
                'loan_id': loan['loan_id'],
                'payment_date': payment_date,
                'amount_paid': round(monthly_due, 2),
                'is_late': is_late
            })
    return pd.DataFrame(repayments)

def load_to_database(df, table_name, engine):
    print(f"Loading {len(df)} records into {table_name}...")
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"Successfully loaded data into {table_name}.")

if __name__ == "__main__":
    # 1. Generate Data
    print("Generating mock data...")
    df_customers = generate_customers(1000)
    df_loans = generate_loans(df_customers)
    df_repayments = generate_repayments(df_loans)
    
    # 2. Database Connection setup
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    
    # SQLAlchemy connection string
    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    # 3. Load Data
    try:
        load_to_database(df_customers, 'customers', engine)
        load_to_database(df_loans, 'loans', engine)
        load_to_database(df_repayments, 'repayments', engine)
        print("Stage 1 Complete: All data loaded to PostgreSQL successfully!")
    except Exception as e:
        print(f"An error occurred while loading data: {e}")