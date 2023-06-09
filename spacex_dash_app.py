# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = int(spacex_df['Payload Mass (kg)'].max())
min_payload = int(spacex_df['Payload Mass (kg)'].min())

launch_site_names = spacex_df['Launch Site'].unique()

# Create a Dash application
app = dash.Dash(__name__)

# Create the app layout
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
        ),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        # dcc.Dropdown(id='site-dropdown',...)

        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                *[
                    {'label': site_name, 'value': site_name}
                    for site_name in launch_site_names
                ]
            ],
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True
        ),
        html.Br(),
        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(
            dcc.Graph(id='success-pie-chart')
        ),
        html.Br(),
        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        #dcc.RangeSlider(id='payload-slider',...)
        dcc.RangeSlider(
            id='payload-slider',
            min=min_payload,
            max=max_payload,
            step=1000,
            marks={str(payload): str(payload) for payload in range(min_payload, max_payload + 1, 1000)},
            value=[min_payload, max_payload]
        ),
        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(
            dcc.Graph(id='success-payload-scatter-chart')
        )
    ]
)
# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Calculate the total success launches for each site
        site_success_counts = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        # Calculate the total failed launches for each site
        site_failed_counts = spacex_df.groupby('Launch Site')['class'].count() - site_success_counts['class']
        
        # Create the pie chart
        fig = go.Figure(data=[go.Pie(
            labels=site_success_counts['Launch Site'],
            values=site_success_counts['class'],
            marker=dict(colors=px.colors.qualitative.Plotly)
        )])

        # Set the chart title
        fig.update_layout(title='Total Launch Success')

        return fig
    else:
        # Filter the DataFrame for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # Calculate success and failed launches for the selected site
        success_count = filtered_df['class'].sum()
        failed_count = len(filtered_df) - success_count

        # Create the pie chart
        labels = ['Success', 'Failed']
        values = [success_count, failed_count]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

        # Set the chart title
        fig.update_layout(title=f'Launch Success - {entered_site}')

        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, selected_payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df[
            (spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
            (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])
        ]
        title = f'Payload Success Rate for All Sites'
    else:
        filtered_df = spacex_df[
            (spacex_df['Launch Site'] == selected_site) &
            (spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
            (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])
        ]
        title = f'Payload Success Rate for {selected_site}'
    scatter_fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title,
        labels={'class': 'Success'},
        hover_data=['Launch Site']
    )

    return scatter_fig

# Run the app
if __name__ == '__main__':
    app.run_server()

