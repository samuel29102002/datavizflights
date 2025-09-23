"""Modernized Dash dashboard for US flight delay analysis."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc

# ---------------------------------------------------------------------------
# Application bootstrap & configuration
# ---------------------------------------------------------------------------
EXTERNAL_STYLESHEETS = [dbc.themes.CYBORG, dbc.icons.FONT_AWESOME]
app: Dash = dash.Dash(__name__, external_stylesheets=EXTERNAL_STYLESHEETS)
app.title = "US Flight Delays – Modern Dashboard"
server = app.server

DATA_URL = (
    "https://gist.githubusercontent.com/florianeichin/"
    "cfa1705e12ebd75ff4c321427126ccee/raw/"
    "c86301a0e5d0c1757d325424b8deec04cc5c5ca9/flights_all_cleaned.csv"
)
MAPBOX_TOKEN = (
    "pk.eyJ1Ijoic2FtYWV6eSIsImEiOiJjbDFtNzYzaWUwMDhpM2twZGxsNGlvZWRwIn0."
    "APwbvxQ3guXJVU6iNKCFFA"
)

# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------
df = pd.read_csv(DATA_URL, encoding="ISO-8859-1")

airline_names = {
    "WN": "Southwest Airlines Co.",
    "DL": "Delta Air Lines Inc.",
    "OO": "SkyWest Airlines Inc.",
    "AA": "American Airlines Inc.",
    "UA": "United Airlines Inc.",
    "EV": "Atlantic Southeast Airlines",
    "US": "US Airways Inc.",
    "B6": "JetBlue Airways",
    "MQ": "American Eagle Airlines Inc.",
    "AS": "Alaska Airlines Inc.",
    "NK": "Spirit Airlines",
    "F9": "Frontier Airlines Inc.",
    "HA": "Hawaiian Airlines Inc.",
    "VX": "Virgin America",
}

df["AIRLINE_NAME"] = df["AIRLINE"].map(airline_names).fillna(df["AIRLINE"])
df["DEPARTURE_DELAY"] = df["DEPARTURE_DELAY"].clip(lower=0)
df["DESTINATION_DELAY"] = df["DESTINATION_DELAY"].clip(lower=0)
df["TOTAL_DELAY"] = (df["DEPARTURE_DELAY"] + df["DESTINATION_DELAY"]).clip(lower=0)
df["MADE_UP_TIME"] = df["SCHEDULED_TIME"] - df["ELAPSED_TIME"]

delay_summary = (
    df.groupby("ORIGIN_AIRPORT")
    .agg(avg_delay=("TOTAL_DELAY", "mean"), flights=("FLIGHT_NUMBER", "count"))
    .reset_index()
)

distance_min = int(df["DISTANCE"].min())
distance_max = int(df["DISTANCE"].max())

px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = px.colors.qualitative.Antique

# ---------------------------------------------------------------------------
# Figure factory helpers
# ---------------------------------------------------------------------------
def create_operations_figure() -> go.Figure:
    fig = go.Figure()
    ordered = delay_summary.sort_values("flights", ascending=False)

    fig.add_bar(
        x=ordered["ORIGIN_AIRPORT"],
        y=ordered["flights"],
        name="Flugaufkommen",
        marker_color="#5bc0de",
        opacity=0.75,
        yaxis="y",
    )
    fig.add_scatter(
        x=ordered["ORIGIN_AIRPORT"],
        y=ordered["avg_delay"],
        name="Durchschnittliche Verspätung",
        mode="lines+markers",
        marker=dict(color="#f0ad4e", size=6),
        line=dict(width=3),
        yaxis="y2",
    )

    fig.update_layout(
        title="Mehr Flüge, mehr Verspätung?",
        margin=dict(t=60, r=30, l=60, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Anzahl Flüge", rangemode="tozero"),
        yaxis2=dict(
            title="Ø Verspätung (min)", overlaying="y", side="right", rangemode="tozero"
        ),
        xaxis=dict(title="Startflughafen", tickangle=-45),
    )
    return fig


def create_map_figure(metric: str) -> go.Figure:
    metric_label = {
        "TOTAL_DELAY": "Gesamtverspätung (min)",
        "DEPARTURE_DELAY": "Abflugverspätung (min)",
        "DESTINATION_DELAY": "Ankunftsverspätung (min)",
    }[metric]

    hover_template = (
        "<b>%{customdata[0]}</b><br>Abflug: %{customdata[1]}<br>"
        "Ankunft: %{customdata[2]}<br>"
        f"{metric_label}: %{{marker.color:.1f}} Minuten"
    )

    fig = go.Figure(
        go.Scattermapbox(
            lat=df["DESTINATION_AIRPORT_LAT"],
            lon=df["DESTINATION_AIRPORT_LON"],
            mode="markers",
            marker=dict(
                color=df[metric],
                colorscale="Plasma",
                sizemode="area",
                size=10 + df[metric].rank(pct=True) * 15,
                opacity=0.85,
                colorbar=dict(title=metric_label),
            ),
            customdata=df[["DESTINATION_AIRPORT", "ORIGIN_AIRPORT", "AIRLINE_NAME"]].values,
            hovertemplate=hover_template,
            showlegend=False,
        )
    )

    fig.update_layout(
        title=f"Verspätungen nach Ziel-Flughafen – {metric_label}",
        mapbox=dict(
            accesstoken=MAPBOX_TOKEN,
            style="dark",
            zoom=2.5,
            center=dict(lat=36.9, lon=-95.8),
        ),
        margin=dict(l=0, r=0, t=60, b=20),
    )
    return fig


def create_histogram(selected_airlines: list[str] | None) -> go.Figure:
    airlines = selected_airlines or sorted(df["AIRLINE_NAME"].unique())
    filtered = df[df["AIRLINE_NAME"].isin(airlines)]
    fig = px.histogram(
        filtered,
        x="DESTINATION_DELAY",
        color="AIRLINE_NAME",
        nbins=40,
        barmode="overlay",
        title="Verteilung der Ankunftsverspätung je Airline",
    )
    fig.update_layout(
        margin=dict(t=60, r=30, l=40, b=60),
        xaxis_title="Verspätung bei Ankunft (min)",
        yaxis_title="Flüge",
        legend_title="Airline",
    )
    return fig


def create_heatmap(distance_range: list[int], selected_airlines: list[str] | None) -> go.Figure:
    airlines = selected_airlines or df["AIRLINE_NAME"].unique()
    filtered = df[
        (df["DISTANCE"].between(distance_range[0], distance_range[1]))
        & (df["AIRLINE_NAME"].isin(airlines))
    ]
    fig = px.density_heatmap(
        filtered,
        x="DISTANCE",
        y="AIRLINE_NAME",
        z="TOTAL_DELAY",
        histfunc="avg",
        color_continuous_scale="Plasma",
        nbinsx=30,
        title="Zusammenhang von Flugdistanz und Verspätung",
    )
    fig.update_layout(
        margin=dict(t=60, r=30, l=60, b=60),
        xaxis_title="Distanz (Meilen)",
        yaxis_title="Airline",
        coloraxis_colorbar=dict(title="Ø Gesamtverspätung (min)"),
    )
    return fig


# ---------------------------------------------------------------------------
# Layout components
# ---------------------------------------------------------------------------
def metric_card(title: str, value: str, icon: str, accent_class: str) -> dbc.Col:
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className=f"{icon} fa-2x me-3 text-{accent_class}"),
                            html.Span(title.upper(), className="card-title"),
                        ],
                        className="d-flex align-items-center",
                    ),
                    html.Div(value, className="metric-value"),
                ]
            ),
            className="metric-card shadow-sm",
        ),
        md=3,
        sm=6,
        xs=12,
    )


def build_layout() -> html.Div:
    avg_departure_delay = f"{df['DEPARTURE_DELAY'].mean():.1f} min"
    avg_arrival_delay = f"{df['DESTINATION_DELAY'].mean():.1f} min"
    total_flights = f"{df['FLIGHT_NUMBER'].count():,}".replace(",", ".")
    recovered_time = f"{df['MADE_UP_TIME'].mean() * -1:.1f} min"

    controls_card = dbc.Card(
        [
            dbc.CardHeader(html.H5("Interaktive Filter", className="mb-0")),
            dbc.CardBody(
                [
                    html.Small("Delay-Metrik für die Karte", className="text-muted fw-semibold"),
                    dcc.Dropdown(
                        id="delay-metric",
                        options=[
                            {"label": "Gesamtverspätung", "value": "TOTAL_DELAY"},
                            {"label": "Abflugverspätung", "value": "DEPARTURE_DELAY"},
                            {"label": "Ankunftsverspätung", "value": "DESTINATION_DELAY"},
                        ],
                        value="TOTAL_DELAY",
                        clearable=False,
                        className="mb-4",
                    ),
                    html.Small("Airlines auswählen", className="text-muted fw-semibold"),
                    dcc.Dropdown(
                        id="airline-dropdown",
                        options=[
                            {"label": name, "value": name}
                            for name in sorted(df["AIRLINE_NAME"].unique())
                        ],
                        value=sorted(df["AIRLINE_NAME"].unique())[:5],
                        multi=True,
                        className="mb-4",
                        placeholder="Airlines wählen",
                    ),
                    html.Small("Distanzfilter (Meilen)", className="text-muted fw-semibold"),
                    dcc.RangeSlider(
                        id="distance-slider",
                        min=distance_min,
                        max=distance_max,
                        step=50,
                        value=[distance_min + 200, distance_max - 400],
                        allowCross=False,
                        tooltip={"placement": "bottom", "always_visible": False},
                        marks={
                            distance_min: str(distance_min),
                            (distance_min + distance_max) // 2: "Ø",
                            distance_max: str(distance_max),
                        },
                    ),
                ]
            ),
        ],
        className="controls-card shadow-sm",
    )

    return dbc.Container(
        [
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.NavbarBrand(
                            [
                                html.I(className="fas fa-plane-departure me-2"),
                                "Flight Delay Insights",
                            ],
                            className="fw-bold",
                        ),
                        html.Span(
                            "US-Flugverspätungen • Januar 2015",
                            className="text-muted small",
                        ),
                    ]
                ),
                dark=True,
                color="rgba(10, 10, 10, 0.6)",
                sticky="top",
                className="mb-4 shadow",
            ),
            dbc.Row(
                [
                    metric_card("Ø Abflugverspätung", avg_departure_delay, "fas fa-clock", "info"),
                    metric_card("Ø Ankunftsverspätung", avg_arrival_delay, "fas fa-hourglass-half", "warning"),
                    metric_card("Flüge insgesamt", total_flights, "fas fa-plane", "primary"),
                    metric_card("Zeit aufgeholt", recovered_time, "fas fa-tachometer-alt", "success"),
                ],
                className="g-4 mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(controls_card, md=4, xs=12, className="mb-4"),
                    dbc.Col(dcc.Graph(id="delay-map", figure=create_map_figure("TOTAL_DELAY")), md=8, xs=12),
                ],
                className="g-4 align-items-stretch",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="airline-histogram", figure=create_histogram(None)), md=6, xs=12),
                    dbc.Col(dcc.Graph(id="distance-heatmap", figure=create_heatmap([distance_min, distance_max], None)), md=6, xs=12),
                ],
                className="g-4 my-2",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=create_operations_figure()), md=12),
                ],
                className="g-4 my-2",
            ),
        ],
        fluid=True,
        className="dashboard-background py-4",
    )


app.layout = build_layout()


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
@app.callback(Output("delay-map", "figure"), Input("delay-metric", "value"))
def update_map(metric: str) -> go.Figure:
    return create_map_figure(metric)


@app.callback(Output("airline-histogram", "figure"), Input("airline-dropdown", "value"))
def update_hist(selected_airlines: list[str] | None) -> go.Figure:
    return create_histogram(selected_airlines)


@app.callback(
    Output("distance-heatmap", "figure"),
    Input("distance-slider", "value"),
    Input("airline-dropdown", "value"),
)
def update_heatmap(distance_range: list[int], selected_airlines: list[str] | None) -> go.Figure:
    return create_heatmap(distance_range, selected_airlines)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True, port=8056)
