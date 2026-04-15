import os
import psycopg2
import pandas as pd
import joblib
import requests

# 1. Configuration & Environment Variables
DB_URL = os.environ.get("DATABASE_URL")
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL")

def run_nightly_risk_assessment():
    print("Starting nightly risk assessment...")
    
    # 2. Dynamically Load the Trained Model
    current_dir = os.path.dirname(__file__)
    model_path = os.path.join(current_dir, 'random_forest_model.pkl')
    
    print(f"Loading model from: {model_path}")
    model = joblib.load(model_path)
    
    # 3. Connect to the Neon Cloud DB
    print("Connecting to Neon Cloud DB...")
    conn = psycopg2.connect(DB_URL)
    
    # 4. Fetch Active Loans 
    # Using 'loan_status' based on your training script schema
    query = "SELECT * FROM vw_loan_portfolio_analytics WHERE loan_status = 'Active';"
    
    # Ignore the Pandas SQLAlchemy warning
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    
    df = pd.read_sql(query, conn)
    
    if df.empty:
        print("No active loans found. Exiting.")
        conn.close()
        return

    print(f"Evaluating {len(df)} active loans...")
    
    # 5. Data Preprocessing (Must match your train_model.py exactly!)
    # Fill blank numerical data with 0 to prevent ML crashes
    df.fillna(0, inplace=True)
    
    # The exact features your model was trained on
    features = [
        'age', 'monthly_income', 'principal_amount', 
        'interest_rate', 'loan_term_months', 'late_payment_count'
    ]
    
    # Run inference: get the probability of the 'Defaulted' class (index 1)
    df['risk_score'] = model.predict_proba(df[features])[:, 1]
    
    # 6. Isolate High-Risk Loans (Threshold set to 85%)
    threshold = 0.85
    high_risk_loans = df[df['risk_score'] >= threshold]
    
    print(f"Identified {len(high_risk_loans)} high-risk loans exceeding the {threshold * 100}% threshold.")
    
    # 7. Push Flags Back to the Database
    if not high_risk_loans.empty:
        cur = conn.cursor()
        
        # Assuming your base table is 'loans' and the primary key is 'loan_id'
        for index, row in high_risk_loans.iterrows():
            # We use try/except here just in case a loan_id is missing
            try:
                update_query = f"UPDATE loans SET high_risk_flag = True WHERE loan_id = '{row['loan_id']}';"
                cur.execute(update_query)
            except Exception as e:
                print(f"Could not update loan {row.get('loan_id', 'Unknown')}: {e}")
                
        conn.commit()
        cur.close()
        print("Successfully updated high_risk_flag in Neon DB.")
        
        # 8. Push Active Alerts to the Credit Team (If webhook is configured)
        if SLACK_WEBHOOK:
            message = {
                "text": f"🚨 *Nightly Risk Alert* 🚨\n{len(high_risk_loans)} loans have crossed the {threshold * 100}% default probability threshold. The executive dashboard has been updated with the new flags."
            }
            requests.post(SLACK_WEBHOOK, json=message)
            print("Team alert dispatched.")
    
    # 9. Clean up
    conn.close()
    print("Nightly risk assessment completed successfully.")

if __name__ == "__main__":
    run_nightly_risk_assessment()