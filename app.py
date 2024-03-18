# %% [markdown]
# Objective: Practice adding callbacks to Dash apps.
#  
# 
# Task:
# (1) Build an app that contains the following components user the gapminder dataset: `gdp_pcap.csv`. 
# TASK 1 is the same as ASSIGNMENT 4. You are welcome to update your code. 
# 
# UI Components:
# A dropdown menu that allows the user to select `country`
# - The dropdown should allow the user to select multiple countries
# - The options should populate from the dataset (not be hard-coded)
# A slider that allows the user to select `year`
# - The slider should allow the user to select a range of years
# - The range should be from the minimum year in the dataset to the maximum year in the dataset
# A graph that displays the `gdpPercap` for the selected countries over the selected years
# - The graph should display the gdpPercap for each country as a line
# - Each country should have a unique color
# - The graph should have a title and axis labels in reader friendly format
#  
# 
# (2) Write Callback functions for the slider and dropdown to interact with the graph
# 
# This means that when a user updates a widget the graph should update accordingly.
# The widgets should be independent of each other. 
# Layout:
# - Use a stylesheet
# - There should be a title at the top of the page
# - There should be a description of the data and app below the title (3-5 sentences)
# - The dropdown and slider should be side by side above the graph and take up the full width of the page
# - The graph should be below the dropdown and slider and take up the full width of the page
# Submission:
# - Deploy your app on Render. 
# - In Canvas, submit the URL to your public Github Repo (made specifically for this assignment)
# - The readme in your GitHub repo should contain the URL to your Render page. 
# **For help you may use the web resources and pandas documentation. No co-pilot or ChatGPT.**

# %%
# Import Libraries
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load csv file
raw_data = pd.read_csv('gdp_pcap.csv')

# check the first 5 rows of the data and the data types
print(raw_data.head())
print(raw_data.dtypes)

# %%
# Melt the DataFrame to reshape it
# https://pandas.pydata.org/docs/reference/api/pandas.melt.html (class example also used melt)
df = raw_data.melt(id_vars=['country'], var_name='year', value_name='gdp')
# turn year to int
df['year'] = df['year'].astype(int)

print(df.head())
print(df.dtypes)

# %%
# Function to convert GDP values to regular numbers
def convert_gdp(gdp_str):
    if isinstance(gdp_str, str) and 'k' in gdp_str:
        return float(gdp_str.replace('k', '')) * 1000
    else:
        return gdp_str

# Apply the function to each GDP value
df['gdp'] = df['gdp'].apply(convert_gdp)

# Convert 'gdp' column to numeric type
df['gdp'] = df['gdp'].astype(int)

# %%
# Make sure the k is removed and converted
# for gdp_value in df['gdp']:
#     print(gdp_value)

# %%
# https://dash.plotly.com/tutorial

# Initialize the app
# style sheet used. followed from the tutorial
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# App layout
app.layout = html.Div([
    # https://dash.plotly.com/dash-html-components
    
    # Title
    html.Div(className='row', children='Assignment 4: Basic UI',
             style={'textAlign': 'center', 'fontFamily': 'Arial', 'color': 'blue', 'fontSize': 25}),
    
    # Paragraph describing the app
    html.P('A dash data application that will display the GDP per capita over time for a given country. The dropdown menu allows users to select multiple countries while the slider allows the user to select a range of years. The data spans from the years 1800-2100. By default, no countries are selected, so we see the overall GDP displayed.',
           style={'textAlign': 'left', 'fontFamily': 'Arial', 'color': 'blue', 'fontSize': 15}),
    
    # https://dash.plotly.com/layout
    # we do six columns to make the dropdown and slider side by side
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[
            # https://dash.plotly.com/dash-core-components/dropdown
            dcc.Dropdown(
                id='countries-dropdown',
                # all the unique countries in the data
                options=[{'label': country, 'value': country} for country in df['country'].unique()],
                # allows you to select multiple countries
                multi=True,
                # placeholder text
                placeholder="Select Country",
                # default 
                value=[]
            ),
        ]),

        html.Div(className='six columns', children=[
            # https://dash.plotly.com/dash-core-components/slider
            dcc.RangeSlider(
                id='year-slider',
                # min and max year values to get the range of years
                min=df['year'].min(),
                max=df['year'].max(),
                # step is 1, so the slider will move by 1 year
                step=1, 
                # Create a label for marks and rotate it 45 degrees
                marks={year: {'label': str(year), 'style': {'transform': 'rotate(45deg)'}}
                       # every 10 years, we will have a mark
                       for year in range(df['year'].min(), df['year'].max() + 1, 10)},
                # default value is the min and max year
                value=[df['year'].min(), df['year'].max()],
                # we dont want the slider to cross
                allowCross=False,
            )
        ])
    ]),
    dcc.Graph(id='gdp-per-capita-graph')
])

# https://dash.plotly.com/basic-callbacks
# Define callback to update the graph based on dropdown selection
@app.callback(
    Output('gdp-per-capita-graph', 'figure'),
    [Input('countries-dropdown', 'value'),
    Input('year-slider', 'value')]
)
# attempted to make the graph update based on the year slider too, but it did not work
def update_graph(selected_countries, selected_years):
    # no countries selected, show overall GDP
    if not selected_countries:
        # filter the data based on the selected years
        filtered_df = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]
        return px.line(filtered_df, x='year', y='gdp', color=None).update_layout(
            # title of the graph
            title='GDP Per Capita Over Time', 
            xaxis_title='Year', 
            yaxis_title='GDP Per Capita',
            template='plotly_white'  
        )
    # make a graph based on the selected countries
    else:
        filtered_df = df[df['country'].isin(selected_countries)]
        # filter the data based on the selected years
        filtered_df = filtered_df[(filtered_df['year'] >= selected_years[0]) & (filtered_df['year'] <= selected_years[1])]
        return px.line(filtered_df, x='year', y='gdp', color='country').update_layout(
            # title of the graph
            title='GDP Per Capita Over Time', 
            xaxis_title='Year',  
            yaxis_title='GDP Per Capita',
            template='plotly_white'
        )

# Run the app
if __name__ == '__main__':
    app.run(jupyter_mode='tab', debug=True)



