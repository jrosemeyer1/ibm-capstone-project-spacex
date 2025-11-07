# spacex_dash_app.py
# Hands-on lab: Interactive Dashboard with Plotly Dash (SpaceX)
# Expected CSV: spacex_launch_dash.csv (same directory)
#
# Tasks implemented:
# - TASK 1: Launch Site dropdown
# - TASK 2: Pie chart callback (success counts / success vs failure per site)
# - TASK 3: Payload RangeSlider
# - TASK 4: Scatter plot callback (payload vs class, colored by booster version)
#
# How to run (after installing deps):
#   python3 spacex_dash_app.py
# Visit http://127.0.0.1:8050/ in your browser.

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

CSV_PATH = "spacex_launch_dash.csv"

try:
    spacex_df = pd.read_csv(CSV_PATH)
except FileNotFoundError as e:
    raise SystemExit(
        f"Could not find {CSV_PATH}. Please download it to the same folder "
        f"and rerun. Original error: {e}"
    )

# Column names used in the IBM course dataset:
# 'Launch Site', 'class', 'Payload Mass (kg)', 'Booster Version Category'

# Derive min/max payload for slider defaults
min_payload = int(spacex_df['Payload Mass (kg)'].min())
max_payload = int(spacex_df['Payload Mass (kg)'].max())

# Build dropdown options (plus "All Sites")
site_options = [{'label': 'All Sites', 'value': 'ALL'}]
site_options += [{'label': site, 'value': site} for site in sorted(spacex_df['Launch Site'].unique())]

app = Dash(__name__)
app.title = "SpaceX Launch Records Dashboard"

app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center'}),

    # ==== TASK 1: Launch Site Drop-down ====
    html.Div([
        html.Label("Launch Site:"),
        dcc.Dropdown(
            id='site-dropdown',
            options=site_options,
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True,
            clearable=False,
            style={'width': '100%'}
        )
    ], style={'padding': '0 20px'}),

    html.Br(),

    # ==== TASK 2: Pie Chart ====
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Hr(),

    # ==== TASK 3: Payload Range Slider ====
    html.Div([
        html.Label("Payload range (Kg):"),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            value=[min_payload, max_payload],
            marks={
                0: '0',
                2500: '2,500',
                5000: '5,000',
                7500: '7,500',
                10000: '10,000'
            },
            tooltip={"placement": "bottom", "always_visible": False}
        )
    ], style={'padding': '0 20px'}),

    html.Br(),

    # ==== TASK 4: Scatter Chart ====
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),

    html.Div(
        "Tip: Use the dropdown and slider to explore how payload and booster version relate to launch success.",
        style={'textAlign': 'center', 'color': '#555', 'padding': '10px 0'}
    )
], style={'maxWidth': '1000px', 'margin': '0 auto'})

# ==== TASK 2: Pie chart callback ====
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Success counts by site (sum of class == 1)
        success_by_site = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            success_by_site,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Success vs Failure counts for the selected site
        site_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Value counts of class (0/1) -> label nicely
        outcome = site_df['class'].value_counts().rename(index={0: 'Failure', 1: 'Success'}).reset_index()
        outcome.columns = ['Outcome', 'Count']
        fig = px.pie(
            outcome,
            values='Count',
            names='Outcome',
            title=f'Launch Outcomes for {selected_site}'
        )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

# ==== TASK 4: Scatter plot callback ====
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)

    if selected_site != 'ALL':
        mask &= (spacex_df['Launch Site'] == selected_site)

    filtered = spacex_df[mask]

    title = 'Payload vs. Outcome (All Sites)'
    if selected_site != 'ALL':
        title = f'Payload vs. Outcome ({selected_site})'

    fig = px.scatter(
        filtered,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=title
    )
    # Improve y-axis readability: 0 -> Failure, 1 -> Success
    fig.update_yaxes(
        tickmode='array',
        tickvals=[0, 1],
        ticktext=['Failure (0)', 'Success (1)']
    )
    return fig

if __name__ == '__main__':
    # Default Dash port: 8050
    app.run(debug=False)
