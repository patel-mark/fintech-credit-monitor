# models/risk_scoring/train_model.py
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# 1. Load environment variables
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

# 2. Fetch Data
print("Fetching analytical data from PostgreSQL...")
query = "SELECT * FROM vw_loan_portfolio_analytics;"
df = pd.read_sql(query, engine)
print(f"Successfully loaded {df.shape[0]} loan records.")

# 3. Data Preprocessing
print("Preprocessing features...")
# Define the columns the model will use to make predictions
features = [
    'age', 'monthly_income', 'principal_amount', 
    'interest_rate', 'loan_term_months', 'late_payment_count'
]

# Create our Target Variable: 1 if Defaulted, 0 otherwise
df['is_default'] = df['loan_status'].apply(lambda x: 1 if x == 'Defaulted' else 0)

# Fill any blank numerical data with 0 to prevent ML crashes
df.fillna(0, inplace=True)

X = df[features]
y = df['is_default']

# Split data: 80% for training the model, 20% for testing it blindly
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train the Model
print("Training Random Forest Classifier...")
# class_weight='balanced' helps the model since 'Defaulted' loans are rarer than good ones
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# 5. Evaluate the Model
print("\n--- Model Evaluation ---")
y_pred = model.predict(X_test)
print(f"Accuracy Score: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
print("Detailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Good Loan (0)', 'Default (1)']))

# 6. Save the Model
os.makedirs('models/risk_scoring', exist_ok=True)
model_path = 'models/risk_scoring/random_forest_model.pkl'
joblib.dump(model, model_path)
print(f"\nModel trained and saved successfully to {model_path}!")