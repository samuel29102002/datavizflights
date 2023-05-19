#imports and stylesheet
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP, 'style.css']


# create dash app, read data and mapboxtoken
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
df = pd.read_csv('https://gist.githubusercontent.com/florianeichin/cfa1705e12ebd75ff4c321427126ccee/raw/c86301a0e5d0c1757d325424b8deec04cc5c5ca9/flights_all_cleaned.csv', encoding="ISO-8859-1")
navbar = dbc.Nav()
token = 'pk.eyJ1Ijoic2FtYWV6eSIsImEiOiJjbDFtNzYzaWUwMDhpM2twZGxsNGlvZWRwIn0.APwbvxQ3guXJVU6iNKCFFA'


# negative delay deleted
df['DELAY'] = df['DEPARTURE_DELAY'] + df['DESTINATION_DELAY']
df['DELAY'] = df['DELAY'].clip(lower=0)


# groupby airport and count them
df2 = pd.DataFrame(df.groupby(by='ORIGIN_AIRPORT')['DEPARTURE_DELAY'].mean())
df2 = df2.reset_index()
counts = df['ORIGIN_AIRPORT'].value_counts()


# airlines and their names
df['AIRLINE'] = df['AIRLINE'].replace('WN', 'Southwest Airlines Co.')
df['AIRLINE'] = df['AIRLINE'].replace('DL', 'Delta Air Lines Inc.')
df['AIRLINE'] = df['AIRLINE'].replace('OO', 'Skywest Airlines Inc.')
df['AIRLINE'] = df['AIRLINE'].replace('AA', 'American Airlines Inc.')
df['AIRLINE'] = df['AIRLINE'].replace('UA', 'United Air Lines Inc.')
df['AIRLINE'] = df['AIRLINE'].replace('EV', 'Atlantic Southeast Airlines')
df['AIRLINE'] = df['AIRLINE'].replace('US', 'US Airways Inc.')
df['AIRLINE'] = df['AIRLINE'].replace('B6', 'JetBlue Airways')
df['AIRLINE'] = df['AIRLINE'].replace('MQ', 'American Eagle Airlines Inc.')
df['AIRLINE'] = df['AIRLINE'].replace('AS', 'Alaska Airlines Inc.')
df['AIRLINE'] = df['AIRLINE'].replace('NK', 'Spirit Air Lines')
df['AIRLINE'] = df['AIRLINE'].replace('F9', 'Frontier Airlines Inc.')
df['AIRLINE'] = df['AIRLINE'].replace('HA', 'Hawaiian Airlines Inc.')
df['AIRLINE'] = df['AIRLINE'].replace('VX', 'Virgin America')


# barchart does airports with more flights have more delay?
bar1 = dcc.Graph(id='bar1',
                 figure={
                     'data': [(go.Scatter(name='Verspätung', x=df2['ORIGIN_AIRPORT'], y=df2['DEPARTURE_DELAY'],  line=dict(color="#ff8800"),  mode='lines', yaxis='y2')),
                              go.Bar(name='Anzahl Flüge', marker_color='slateblue', x=counts.index, y=counts.values, yaxis='y')],
                     'layout': {'title': dict(
                         text='Wirkt sich ein hoher Flugbetrieb auf große Verspätungen aus?',
                         font=dict(size=20,
                                   color='white')),
                                "paper_bgcolor": "black",
                                "plot_bgcolor": "black",
                                'height': 600,
                                "line": dict(
                         color="white",
                         width=4,
                         dash="dash",),
                         'xaxis': dict(tickfont=dict(
                             color='white'), showgrid=False, title='Flughäfen', color='white'),
                         'yaxis': dict(tickfont=dict(
                             color='white'), showgrid=False, title='Anzahl Flüge', color='white', rangemode="tozero"),
                         'yaxis2': dict(tickfont=dict(
                             color='white'), showgrid=False, title='Verspätung in min', color='white', overlaying='y', side='right', rangemode="tozero")
                     }})


# negative seperatet delay deleted
df['DEPARTURE_DELAY'] = df['DEPARTURE_DELAY'].clip(lower=0)
df['DESTINATION_DELAY'] = df['DESTINATION_DELAY'].clip(lower=0)
  


# create mapbox figure
fig = go.Figure()
a = go.Scattermapbox(
    lat=df['DESTINATION_AIRPORT_LAT'],
    lon=df['DESTINATION_AIRPORT_LON'],

    mode="markers",
    marker=go.scattermapbox.Marker(
        size=df['DELAY'].mean()/2,
        color=df['DELAY'],
        cmax=100,
        cmin=10,
        colorscale="oranges",
        showscale=True,

    ), name='DESTINATION',)
fig.add_trace(a)


# finetuning mapbox figure

fig.update_layout(
    mapbox_style="dark",
    mapbox_accesstoken=token,
    title='Durchschnittliche Verspätungen in Minuten nach Flughäfen',
    paper_bgcolor="rgb(1,1,1,1)",
    plot_bgcolor="rgb(1,1,1,1)",
    autosize=True,

    hovermode='closest',
    margin={"r": 0, "t": 50, "l": 0, "b": 50},
    mapbox_zoom=2,
    font=dict(size=18,
              color='white'),
    mapbox_center={"lat": 36.966428, "lon": -95.844032})
fig.update_mapboxes(pitch=30)


# airlines with more delay than other because of there comfort and prizes?
fig1 = go.Figure()
for n in df[df['DESTINATION_DELAY'] < 60].groupby('AIRLINE'):
    fig1.add_trace(go.Histogram(
        x=n[1].DESTINATION_DELAY, name=n[0], xbins=dict(size=20), opacity=1))


# finetuning airline figure
fig1.update_layout(
    title_text='Verspätung je Airline in 20min Schritten',  # title of plot
    paper_bgcolor="rgb(1,1,1,1)",
    plot_bgcolor="rgb(1,1,1,1)",
    height=600,
    font=dict(size=14,
               color='white'),
    xaxis=dict(tickfont=dict(
        color='white'), showgrid=False, title='Verspätungszeitraum', color='white'),
    yaxis=dict(tickfont=dict(
        color='white'), showgrid=False, title='Verspätung', color='white', rangemode="tozero"),
    bargap=0.2,  # gap between bars of adjacent location coordinates
    bargroupgap=0.1)  # gap between bars of the same location coordinatesit
fig1.update_xaxes(showticklabels=False)


# does longer flights have more delay than short flights?
fig2 = go.Figure(
    go.Heatmap(z=df['DELAY'], x=df['DISTANCE'], y=df['AIRLINE'], hoverongaps=False, zmin=10, zmax=100, colorscale="oranges_r"))

# finetuning distance figure
fig2.update_layout(
    title_text='Wirkt sich eine höhere Distanz auf die Verspätungen aus?',
    paper_bgcolor="rgb(1,1,1,1)",
    plot_bgcolor="rgb(1,1,1,1)",
    font=dict(size=14,
               color='white'),

    height=600,
    xaxis=dict(tickfont=dict(
        color='white'), showgrid=False, title='Flugdistanz', color='white'),
    yaxis=dict(tickfont=dict(
        color='white'), showgrid=False, title='Airline', color='white', rangemode="tozero"),
    yaxis_nticks=0, xaxis_nticks=10)


# set indicators with the important key facts
fig3 = go.Figure()
fig3.add_trace(go.Indicator(
    mode="gauge+number",
    number={'suffix': " min"},
    value=df['DESTINATION_DELAY'].mean(),
    gauge={'axis': {'range': [None, 20],
                    'tickwidth': 1}, 'bar': {'color': "darkorange"}},
    domain={'row': 1, 'column': 1}))
fig3.update_layout(paper_bgcolor="rgb(1,1,1,1)",
                   plot_bgcolor="rgb(1,1,1,1)",
                   title={'text': "Durchschnittliche Verspätung",
                          'font': {'size': 18}},
                   font=dict(size=14, color='white'),)


# set indicators with the important key facts
fig4 = go.Figure()
fig4.add_trace(go.Indicator(
    mode="number",
    number={'valueformat': '.'},
    value=df['FLIGHT_NUMBER'].count(),
    gauge={'axis': {'range': [None, 15000],
                    'tickwidth': 1}, 'bar': {'color': "red"}},
    domain={'row': 1, 'column': 1}))
fig4.update_layout(paper_bgcolor="rgb(1,1,1,1)",
                   plot_bgcolor="rgb(1,1,1,1)",
                   title={'text': "Anzahl aller Flüge vom 01.01.2015",
                          'font': {'size': 18, 'color': 'white'}},
                   font=dict(size=14, color='ghostwhite'),)


# add mean flight time delta
df['FLIGHT_TIME_DELTA'] = df['ELAPSED_TIME'].mean()-df['SCHEDULED_TIME'].mean()


# set indicators with the important key facts
fig5 = go.Figure()
fig5.add_trace(go.Indicator(
    mode="number",
    value=df['FLIGHT_TIME_DELTA'].mean()*-1,
    number={'suffix': " min"},
    gauge={'axis': {'range': [None, 10],
                    'tickwidth': 1}, 'bar': {'color': "red"}},
    domain={'row': 1, 'column': 1}))
fig5.update_layout(paper_bgcolor="rgb(1,1,1,1)",
                   plot_bgcolor="rgb(1,1,1,1)",
                   title={'text': "Durchschnittlich aufgeholte Zeit in der Luft",
                          'font': {'size': 18, 'color': 'white'}},
                   font=dict(size=14, color='limegreen'),)


# initialize the dash graphics and arrange them to the dashboard
flightmap = dcc.Graph(figure=fig)
histo = dcc.Graph(figure=fig1)
heat = dcc.Graph(figure=fig2)
indicator = dcc.Graph(figure=fig3)
indicator1 = dcc.Graph(figure=fig4)
indicator2 = dcc.Graph(figure=fig5)
graphRow1 = dbc.Row([dbc.Col(flightmap, md=12)])
graphRow2 = dbc.Row([dbc.Col(bar1, md=12)])
graphRow3 = dbc.Row([dbc.Col(histo, md=6), dbc.Col(heat, md=6)])
graphRow4 = dbc.Row([dbc.Col(indicator1, md=4), dbc.Col(
    indicator, md=4), dbc.Col(indicator2, md=4)])


# forming the dashboard
app.layout = html.Div([navbar, html.Br(), graphRow4, html.Br(
), graphRow1, html.Br(), graphRow3, html.Br(), graphRow2], style={'backgroundColor': 'lightgrey'})


# run dash app
if __name__ == '__main__':
    app.run_server(debug=True, port=8056)
