import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import psycopg2
import os

# -------------------------------------------------------------------------
# 1. INITIALIZE APP (Switched to LUMEN Light Theme)
# -------------------------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])
server = app.server 

# -------------------------------------------------------------------------
# 2. LOAD & PREP DATA FROM NEON CLOUD
# -------------------------------------------------------------------------
NEON_DB_URL = os.environ.get("DATABASE_URL") 
df = pd.DataFrame() # Fallback

try:
    if NEON_DB_URL:
        conn = psycopg2.connect(NEON_DB_URL)
        query = "SELECT * FROM vw_loan_portfolio_analytics;"
        df = pd.read_sql(query, conn)
        conn.close()
    else:
        print("Warning: DATABASE_URL not found.")

except Exception as e:
    print(f"Database connection failed: {e}")

# --- PANDAS DATA TRANSFORMATIONS ---
if not df.empty:
    # 1. Recreate the 'Income Bracket' DAX Column
    def categorize_income(income):
        if pd.isna(income): return "Other"
        elif income < 50000: return "1. Low Income (< 50K)"
        elif income <= 150000: return "2. Middle Income (50K - 150K)"
        else: return "3. High Income (> 150K)"
    
    if 'monthly_income' in df.columns:
        df['Income Bracket'] = df['monthly_income'].apply(categorize_income)
    else:
        df['Income Bracket'] = "Other"

    # 2. Recreate the "Default Rate" DAX Measure logic!
    # Assigns 1 if Defaulted, 0 otherwise. The 'average' of this is the default rate.
    if 'loan_status' in df.columns:
        df['is_default'] = df['loan_status'].apply(lambda x: 1 if str(x).strip().lower() == 'defaulted' else 0)

    # Force loan_term_months to be a string so heatmaps treat it as a category, not a continuous number
    if 'loan_term_months' in df.columns:
        df['loan_term_months'] = df['loan_term_months'].astype(str)

    # 3. Map coordinates
    coords = {
        'Nairobi': (-1.2921, 36.8219),
        'Mombasa': (-4.0435, 39.6682),
        'Kisumu': (-0.0917, 34.7680),
        'Nakuru': (-0.3031, 36.0800)
    }
    if 'location_county' in df.columns:
        df['Lat'] = df['location_county'].map(lambda x: coords.get(x, (0,0))[0])
        df['Lon'] = df['location_county'].map(lambda x: coords.get(x, (0,0))[1])

    # 4. Extract Month
    if 'disbursement_date' in df.columns:
        df['disbursement_date'] = pd.to_datetime(df['disbursement_date'])
        df['Month'] = df['disbursement_date'].dt.strftime('%B')
        df['Month_Num'] = df['disbursement_date'].dt.month
        df = df.sort_values('Month_Num')

# -------------------------------------------------------------------------
# 3. CREATE FIGURES (With Light Theme Formatting)
# -------------------------------------------------------------------------
# Swapped plotly_dark to plotly_white
light_layout = dict(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20))
empty_fig = go.Figure().update_layout(**light_layout)

if not df.empty:
    trend_col = 'principal_amount' if 'principal_amount' in df.columns else 'total_amount'
    
    # Fig 1: Trend Bar Chart
    trend_df = df.groupby('Month')[trend_col].sum().reset_index()
    trend_fig = px.bar(trend_df, x='Month', y=trend_col, color_discrete_sequence=['#4A90E2']).update_layout(**light_layout)

    # Fig 2: Location Map (Switched mapbox_style to carto-positron for light mode)
    map_fig = px.scatter_mapbox(df, lat="Lat", lon="Lon", color="loan_status", size=trend_col, hover_name="location_county",
                                color_discrete_map={'Active': '#00B894', 'Closed': '#0984E3', 'Defaulted': '#D63031'},
                                mapbox_style="carto-positron", zoom=5, center={"lat": -0.0236, "lon": 37.9062}).update_layout(**light_layout)

    # Fig 3 & 4: Heatmaps (Now using 'is_default' to calculate the real rates!)
    if 'is_default' in df.columns and 'employment_status' in df.columns and 'loan_term_months' in df.columns:
        emp_heat_fig = px.density_heatmap(df, x="loan_term_months", y="employment_status", z="is_default", histfunc="avg", 
                                          color_continuous_scale="Reds", text_auto=".2f").update_layout(**light_layout)
    else: 
        emp_heat_fig = empty_fig

    if 'is_default' in df.columns and 'Income Bracket' in df.columns and 'loan_term_months' in df.columns:
        inc_heat_fig = px.density_heatmap(df, x="loan_term_months", y="Income Bracket", z="is_default", histfunc="avg", 
                                          color_continuous_scale="Reds", text_auto=".2f").update_layout(**light_layout)
    else: 
        inc_heat_fig = empty_fig

else:
    trend_fig, map_fig, emp_heat_fig, inc_heat_fig = empty_fig, empty_fig, empty_fig, empty_fig

# -------------------------------------------------------------------------
# 4. HELPER FUNCTION: KPI CARD GENERATOR (Light Theme)
# -------------------------------------------------------------------------
def create_kpi_card(title, value, id_suffix):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title text-muted text-center fw-bold"),
            html.H3(value, id=f"kpi-{id_suffix}", className="text-center text-dark")
        ]),
        className="mb-3 shadow-sm border-0", style={"backgroundColor": "#ffffff"}
    )

# -------------------------------------------------------------------------
# 5. APP LAYOUT
# -------------------------------------------------------------------------
app.layout = dbc.Container([
    # Header Ribbon
    dbc.Row([
        dbc.Col(html.H2("FinTech Credit Risk Monitor", className="text-dark p-3 m-0"), width=12, 
                style={"backgroundColor": "#ffffff", "borderBottom": "3px solid #72393F", "boxShadow": "0 2px 4px rgba(0,0,0,0.05)"})
    ], className="mb-4"),

    # KPI Cards
    dbc.Row([
        dbc.Col(create_kpi_card("Total Disbursed", "547.13M", "disbursed"), width=True),
        dbc.Col(create_kpi_card("Active Loans", "1.05K", "active"), width=True),
        dbc.Col(create_kpi_card("Total Outstanding", "255.76M", "outstanding"), width=True),
        dbc.Col(create_kpi_card("Default Rate", "10.25%", "default"), width=True),
        dbc.Col(create_kpi_card("Avg Interest Rate", "17.50%", "interest"), width=True),
    ], className="mb-4"),

    # Top Visuals
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("Disbursement Trend", className="fw-bold bg-white"), dbc.CardBody(dcc.Graph(figure=trend_fig, style={'height': '350px'}))], className="shadow-sm border-0"), width=7),
        dbc.Col(dbc.Card([dbc.CardHeader("Total Outstanding by Location", className="fw-bold bg-white"), dbc.CardBody(dcc.Graph(figure=map_fig, style={'height': '350px'}))], className="shadow-sm border-0"), width=5)
    ], className="mb-4"),

    # Bottom Visuals
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("Risk Concentration by Employment Status", className="fw-bold bg-white"), dbc.CardBody(dcc.Graph(figure=emp_heat_fig, style={'height': '300px'}))], className="shadow-sm border-0"), width=6),
        dbc.Col(dbc.Card([dbc.CardHeader("Risk Concentration by Income Segment", className="fw-bold bg-white"), dbc.CardBody(dcc.Graph(figure=inc_heat_fig, style={'height': '300px'}))], className="shadow-sm border-0"), width=6)
    ], className="mb-4")

], fluid=True, style={"backgroundColor": "#f4f6f8", "minHeight": "100vh", "paddingBottom": "50px"})

if __name__ == '__main__':
    app.run(debug=True)