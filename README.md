***

# 🚀 FinTech Credit Risk Monitor & Data Pipeline

An end-to-end, cloud-native data pipeline and machine learning architecture I built to monitor loan portfolios, predict credit defaults, and deliver real-time executive analytics. 

By migrating from a local data architecture to a fully decoupled cloud ecosystem, I transformed raw simulated transaction data into a live, scalable web service and an automated predictive alerting system.

## 🏗️ Architecture Overview

I designed this project using a modern, triple-branch consumption architecture to ensure the database acts as a single source of truth powering multiple distinct business needs.

![Project Architecture](https://i.postimg.cc/RVVG8JTY/Untitled-Diagram.webp)

### 1. Ingestion & Staging Layer
* **Data Sources:** I simulated a realistic FinTech environment with a Loan Database and a live Transaction API.
* **ETL Pipeline:** I wrote a custom Python ETL script (`elt/src/generate_data.py`) to extract this raw data, transform it, and load it into my **Local Staging DB** (PostgreSQL) for initial cleaning and validation.

### 2. Cloud Data Warehouse & Abstraction
* **Neon Cloud DB:** I migrated the staged data to **Neon**, a serverless, globally accessible PostgreSQL cloud database. 
* **Analytics Views:** To protect the raw data and prevent complex runtime joins, I built an abstraction layer. I created the `vw_loan_portfolio_analytics` SQL view to serve as the clean, highly optimized dataset for all downstream applications.

### 3. The Triple-Branch Consumption Layer
I engineered the data to flow into three specialized consumption endpoints:
1. **Executive Deep-Dives (Power BI):** A comprehensive dashboard for high-level historical reporting and complex DAX-based financial metric tracking.
2. **Live Web Operations (Python Dash + Docker + Render):** I built a responsive web application (`dashboard/dash_app/app.py`) using Pandas and Plotly. I containerized this app using **Docker** and **Gunicorn**, bypassing local network constraints, and deployed it as a live Web Service on **Render** for 24/7 browser access.
3. **Automated Risk Alerts (Machine Learning):** I trained a Random Forest Classifier (`models/risk_scoring/train_model.py`) to predict the probability of loan defaults based on key financial markers. 

## 🧠 The Predictive Machine Learning Engine

Instead of running the ML model manually, I deployed the inference script (`models/risk_scoring/run_model.py`) as an isolated **Cron Job on Render**. 

Every night at midnight, this automated worker:
1. Wakes up and connects securely to the Neon Cloud DB.
2. Downloads the latest active loan data from the analytics view.
3. Evaluates the portfolio using the trained Random Forest `.pkl` model.
4. Identifies any loans breaching the **85% default probability threshold**.
5. Automatically flags these high-risk loans back in the Neon database (instantly updating the Dash web app) and dispatches active Webhook alerts directly to the credit team.

## 🛠️ Tech Stack
* **Languages:** Python 3, SQL
* **Data Engineering:** Pandas, Psycopg2, PostgreSQL
* **Cloud Infrastructure:** Neon (Serverless Postgres), Render (Web Services & Cron Jobs)
* **DevOps:** Docker, Gunicorn, Git
* **Machine Learning:** Scikit-Learn, Joblib
* **Data Visualization:** Dash, Plotly, Bootstrap, Power BI

## ⚙️ How to Run This Project Locally

If you want to clone this repository and run the architecture on your own machine:

**1. Clone the repository and install dependencies:**
```bash
git clone https://github.com/patel-mark/fintech-credit-monitor.git
cd fintech-credit-monitor
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Environment Variables:**
You will need to set your database connection string to point to your own Postgres instance. 
```bash
export DATABASE_URL="postgresql://user:password@host:port/dbname"
```

**3. Run the Web Dashboard via Docker:**
```bash
docker build --network=host -t fintech-dashboard .
docker run --network=host -e DATABASE_URL=$DATABASE_URL -e PYTHONUNBUFFERED=1 fintech-dashboard
```
*The dashboard will be available at `http://localhost:8000`.*

**4. Trigger the ML Nightly Risk Assessment:**
```bash
python models/risk_scoring/run_model.py
```
