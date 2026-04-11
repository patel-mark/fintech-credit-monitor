# dashboard/dash_app/app.py
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import dash
from dash import dcc, html
import plotly.express as px

# 1. Connect to Cloud Database
load_dotenv()
connection_string = os.getenv("DATABASE_URL")
engine = create_engine(connection_string)

print("Fetching live data from the cloud...")
df = pd.read_sql("SELECT * FROM vw_loan_portfolio_analytics", engine)

# 2. Calculate KPIs
total_principal = df['principal_amount'].sum()
total_outstanding = df['outstanding_balance'].sum()
default_rate = (len(df[df['loan_status'] == 'Defaulted']) / len(df)) * 100

# 3. Dusk Color Palette & Styling
theme = {
    'darkest': '#29090A',   # Deep rich dark brown/black (Text)
    'primary': '#72393F',   # Dusky red (Defaults - draws attention)
    'secondary': '#A9634A', # Muted rust (Closed)
    'accent': '#9E8AB4',    # Dusky purple (Active)
    'card_bg': '#D3DBE6',   # Soft blue-gray (Cards)
    'bg': '#EFF0EB'         # Off-white background
}

# Explicitly map statuses to colors so they remain consistent across all graphs
status_colors = {
    'Active': theme['accent'],
    'Closed': theme['secondary'],
    'Defaulted': theme['primary']
}

# 4. Initialize Dash App
app = dash.Dash(__name__)
server = app.server

# Helper function to apply a clean, smooth aesthetic to all graphs
def apply_smooth_layout(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', # Transparent to blend with card
        plot_bgcolor='rgba(0,0,0,0)', 
        font_color=theme['darkest'],
        font_family="Segoe UI, Tahoma, sans-serif",
        margin=dict(l=40, r=40, t=60, b=40),
        hoverlabel=dict(bgcolor=theme['card_bg'], font_size=14, font_family="Segoe UI"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor='rgba(211, 219, 230, 0.5)', zeroline=False) # Soft gridlines
    return fig

# 5. Create Visualizations
fig_status = px.pie(
    df, names='loan_status', title='Portfolio Health by Loan Status',
    color='loan_status', color_discrete_map=status_colors, hole=0.45
)
fig_status = apply_smooth_layout(fig_status)
fig_status.update_traces(marker=dict(line=dict(color='#FFFFFF', width=2)))

fig_scatter = px.scatter(
    df, x='monthly_income', y='principal_amount', color='loan_status',
    title='Income vs. Loan Size', opacity=0.75,
    labels={'monthly_income': 'Monthly Income (KES)', 'principal_amount': 'Principal Amount (KES)', 'loan_status': 'Loan Status'},
    color_discrete_map=status_colors
)
fig_scatter = apply_smooth_layout(fig_scatter)
fig_scatter.update_traces(marker=dict(size=9, line=dict(width=0.5, color=theme['darkest'])))

fig_county = px.histogram(
    df, x='location_county', color='loan_status', barmode='group',
    title='Loan Distribution by County',
    color_discrete_map=status_colors,
    labels={'location_county': 'County', 'loan_status': 'Loan Status'}
)
fig_county = apply_smooth_layout(fig_county)
fig_county.update_traces(marker_line_width=0)

# Reusable CSS blocks for clean layout
card_style = {
    'flex': '1', 
    'padding': '24px', 
    'backgroundColor': theme['card_bg'], 
    'borderRadius': '16px', 
    'boxShadow': '0 10px 20px -5px rgba(41, 9, 10, 0.1)', 
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'center',
    'alignItems': 'center'
}

graph_card_style = {
    'backgroundColor': '#FFFFFF', 
    'borderRadius': '16px', 
    'overflow': 'hidden', 
    'boxShadow': '0 10px 20px -5px rgba(41, 9, 10, 0.08)',
    'padding': '15px'
}

# 6. Build the Layout
app.layout = html.Div(style={'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', 'padding': '40px', 'backgroundColor': theme['bg'], 'minHeight': '100vh'}, children=[
    
    html.H1("FinTech Credit Risk Monitor", style={'textAlign': 'center', 'color': theme['darkest'], 'fontWeight': '800', 'letterSpacing': '-0.5px', 'marginBottom': '40px'}),
    
    # KPI Cards
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '24px', 'marginBottom': '40px'}, children=[
        html.Div(style=card_style, children=[
            html.H4("Total Disbursed", style={'color': theme['darkest'], 'margin': '0 0 10px 0', 'fontWeight': '600', 'textTransform': 'uppercase', 'fontSize': '14px', 'letterSpacing': '1px'}), 
            html.H2(f"KES {total_principal:,.0f}", style={'color': theme['accent'], 'margin': '0', 'fontSize': '32px'})
        ]),
        html.Div(style=card_style, children=[
            html.H4("Total Outstanding", style={'color': theme['darkest'], 'margin': '0 0 10px 0', 'fontWeight': '600', 'textTransform': 'uppercase', 'fontSize': '14px', 'letterSpacing': '1px'}), 
            html.H2(f"KES {total_outstanding:,.0f}", style={'color': theme['secondary'], 'margin': '0', 'fontSize': '32px'})
        ]),
        html.Div(style=card_style, children=[
            html.H4("Default Rate", style={'color': theme['darkest'], 'margin': '0 0 10px 0', 'fontWeight': '600', 'textTransform': 'uppercase', 'fontSize': '14px', 'letterSpacing': '1px'}), 
            html.H2(f"{default_rate:.2f}%", style={'color': theme['primary'], 'margin': '0', 'fontSize': '32px'})
        ]),
    ]),
    
    # Charts Row 1
    html.Div(style={'display': 'flex', 'gap': '24px', 'marginBottom': '24px'}, children=[
        html.Div([dcc.Graph(figure=fig_status, config={'displayModeBar': False})], style={**graph_card_style, 'width': '35%'}),
        html.Div([dcc.Graph(figure=fig_scatter, config={'displayModeBar': False})], style={**graph_card_style, 'width': '65%'}),
    ]),
    
    # Charts Row 2
    html.Div(style=graph_card_style, children=[
        dcc.Graph(figure=fig_county, config={'displayModeBar': False})
    ])
])

if __name__ == '__main__':
    app.run(debug=True, port=8050)