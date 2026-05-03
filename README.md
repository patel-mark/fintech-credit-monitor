# FinTech Credit Risk Monitor & Data Pipeline

![Build Status](https://img.shields.io/badge/Status-Complete-success) ![Python](https://img.shields.io/badge/Python-3.12-blue) ![PostgreSQL](https://img.shields.io/badge/Database-Neon_Postgres-blue) ![Deployment](https://img.shields.io/badge/Deploy-Docker%20%7C%20Render-blue)

![Executive Dashboard](https://i.postimg.cc/jj6qCCz3/Fin-Tech-Credit-Risk-Dashboard-(5).png)

## 📖 Overview & Business Problem
Financial institutions face significant exposure to preventable loan defaults. The primary challenge is migrating from reactive, historical reporting to a proactive, real-time alerting system that identifies high-risk credit profiles *before* a default occurs. 

This end-to-end cloud-native data pipeline and machine learning architecture transforms raw simulated financial data into an automated, executive-facing dashboard. By predicting the exact probability of default for active loans and moving the entire infrastructure to a serverless cloud environment, risk management teams can deploy surgical, high-ROI interventions to protect the firm's capital.

## 🎯 Objectives
1. **Cloud Data Migration:** Modernize the data architecture by migrating local staging databases to a globally accessible, serverless Neon PostgreSQL Cloud Data Warehouse.
2. **Interactive Live BI:** Develop an analyst-friendly Python Dash web app and Power BI Dashboard to track portfolio health and monitor model predictions.
3. **Automated Risk Prediction:** Build and deploy a predictive Random Forest classification model as a serverless Cron Job to continuously evaluate live loans.

## 📊 Key Executive Insights (Power BI Dashboard Analysis)
1. **Portfolio Health & Financial Exposure** (The "What")
Analysis of the loan portfolio between April 2024 and April 2026 reveals a total disbursed amount of **547.13M**, with **255.76M** currently sitting as Total Outstanding across 1.05K active loans. The baseline default rate sits at **10.25%** with an average interest rate of 17.50%. This indicates that roughly ~26M in active capital is highly exposed if current default trends continue unmitigated.

2. **Risk Concentration by Employment Status** (The "Who")
While "Salaried" individuals make up the vast majority of the outstanding balance, the risk density lies elsewhere. The risk heatmaps clearly identify that **Unemployed borrowers on 6-month loan terms** present the absolute highest isolated risk profile across the entire portfolio, surging to a **21% (0.21) default rate**.

3. **Risk Concentration by Income Segment** (The "Where")
The "Middle Income" bracket (50K - 150K) holds the highest overall principal amount. However, an anomaly was detected in their term preferences: Middle-income borrowers utilizing **12-month loan terms** display an unusually elevated default rate of **17% (0.17)**, which is significantly higher than their 6-month or 24-month counterparts in the same income bracket. 

4. **Strategic Action Plan** (The "How")
Based on this analysis, broad-spectrum risk policies are inefficient. Instead, I deployed the Machine Learning pipeline to aggressively flag and monitor two specific micro-segments: Unemployed 6-month loans and Middle-Income 12-month loans. By integrating this intelligence into the nightly ML Cron Job, the credit team receives targeted alerts on these specific high-risk profiles *before* they cross the point of no return.

## 🏗️ Architecture & Workflow

![Architecture Flow](https://i.postimg.cc/RVVG8JTY/Untitled-Diagram.webp)

The pipeline is built for scalability, utilizing a modern triple-branch consumption architecture:
1. **Ingestion & Staging Layer:** A custom Python ETL script extracts simulated loan and transaction data, transforming and loading it into a Local Staging DB for validation.
2. **Cloud Data Warehouse & Abstraction:** Data is pushed to the serverless **Neon Cloud DB**. A custom SQL view (`vw_loan_portfolio_analytics`) abstracts complex joins, securing raw data and optimizing downstream queries.
3. **Branch 1 - Deep Analytics:** Power BI connects directly to the Neon view for heavy executive monitoring and historical segment tracking.
4. **Branch 2 - Live Web Ops:** A Python Dash app, containerized with **Docker** and **Gunicorn**, runs as a 24/7 web service on **Render**.
5. **Branch 3 - Predictive AI:** A Random Forest model runs as an isolated Render **Cron Job**, evaluating the database nightly and writing high-risk flags back to the database to update the dashboard.

## 🚀 Key Features & Advanced Concepts
* **Serverless Cloud Infrastructure:** Completely decoupled the database from the application using Neon Postgres, allowing infinite scaling and remote access without local firewall blocks.
* **Docker Containerization:** Eliminated "it works on my machine" issues by packaging the Dash web application inside a lightweight, host-networked Docker container.
* **Automated ML Orchestration:** Deployed the machine learning inference script as a cloud-native Cron Job, bypassing the need for heavy orchestration tools like Airflow for a targeted task.
* **Dynamic Environment Variables:** Secured all database credentials and API keys using strict environment variable injection (`os.environ.get`) across both local and cloud environments.

## 🛠️ Tech Stack
* **Data Science & ML:** Python, Pandas, Scikit-Learn, Joblib
* **Database & Querying:** PostgreSQL, Neon Serverless Postgres, SQL
* **Cloud & DevOps:** Docker, Gunicorn, Render (Web Services & Cron Jobs), Git
* **Data Visualization:** Power BI, Dash, Plotly

## 📂 Repository Structure
```text
├── elt/
│   └── src/                  # Python ETL scripts for simulated data generation
├── models/
│   └── risk_scoring/         # ML training script, nightly inference script, and .pkl model
├── dashboard/
│   └── dash_app/             # Dash web app, Dockerfile, and layout components
├── requirements.txt          # Shared Python dependencies for Render deployments
└── README.md                 # Project documentation
```

## 📈 Business Impact
This architecture directly informs targeted risk mitigation and capital preservation. By fully automating the ingestion, visualization, and predictive modeling processes, the firm eliminates manual reporting delays. Highlighting critical risk pockets—such as the 21% default rate in 6-month unemployed loans—allows the credit team to adjust underwriting policies and drastically improve their ability to intercept high-risk accounts before default.

---
## 👨‍💻 Author
**Mark Patel** | [LinkedIn Profile](https://www.linkedin.com/in/mark-patel-in-data001/) | [GitHub Profile](https://github.com/patel-mark)
