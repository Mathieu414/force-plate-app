from dash import Input, Output, State, callback, ctx, no_update, html, dcc, dash_table
import dash_bootstrap_components as dbc
from components import (
    ValueCard,
)
import plotly.graph_objects as go
import pandas as pd
from utils.utils import generate_graph, generate_table_data

height = 50

MetricsTabContent = dbc.Row(
    children=[
        dbc.Col(
            [
                dbc.Row(
                    children=[
                        dbc.Col(
                            ValueCard(
                                0,
                                "N",
                                "Force moyenne",
                                "session-force-card",
                                height=height / 2,
                                h3_size="2vw",
                                h2_size="1vw",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            ValueCard(
                                0,
                                "m/s",
                                "Vitesse moyenne",
                                "session-speed-card",
                                height=height / 2,
                                h3_size="2vw",
                                h2_size="1vw",
                            ),
                            width=6,
                        ),
                    ],
                    class_name="mb-2",
                ),
                dbc.Row(
                    dbc.Col(
                        ValueCard(
                            0,
                            "watt",
                            "Puissance",
                            "session-power-card",
                            height=height / 2,
                            h3_size="2vw",
                            h2_size="1vw",
                        ),
                        width=6,
                    ),
                    justify="center",
                ),
            ],
            width=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    children=[
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    children=[
                                        dbc.Button(
                                            html.I(className="fas fa-list"),
                                            size="sm",
                                            id="choice-list",
                                        ),
                                        dbc.Button(
                                            html.I(className="fas fa-chart-line"),
                                            size="sm",
                                            id="choice-chart",
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    html.H5(
                                        "Résumé de la séance",
                                        className="text-center",
                                    ),
                                ),
                                dbc.Col(
                                    children=[
                                        dbc.Button(
                                            "N",
                                            id="type-force",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "M/S",
                                            id="type-speed",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "Watt",
                                            id="type-power",
                                            size="sm",
                                        ),
                                    ],
                                    class_name="text-end",
                                    id="units-buttons",
                                ),
                            ],
                            justify="between",
                        ),
                        html.Div(
                            id="session-display",
                            style={"height": str(height) + "vh"},
                            children=[
                                html.Div(
                                    id="session-display-graph",
                                    children=[
                                        dcc.Graph(
                                            id="session-summary-chart",
                                            style={"height": str(height) + "vh"},
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id="session-display-table",
                                    children=[
                                        html.H4(
                                            "Données de la séance",
                                            className="text-center",
                                        ),
                                        dash_table.DataTable(
                                            id="datatable-session",
                                            editable=True,
                                            row_deletable=True,
                                            export_format="xlsx",
                                            style_table={
                                                "height": str(height * 10) + "px",
                                                "overflowY": "auto",
                                            },
                                        ),
                                    ],
                                    className="mt-3",
                                    style={"display": "none"},
                                ),
                            ],
                        ),
                        dbc.Button(
                            id="reset-session-data",
                            children="Remettre à zéro",
                            color="danger",
                        ),
                    ]
                )
            ),
            width=8,
        ),
    ],
    class_name="m-2",
)


""" @callback(
    Output("session-summary-chart", "figure"),
    Output("session-display-graph", "style"),
    Output("datatable-session", "data"),
    Output("session-display-table", "style"),
    Output("session-display-type", "data"),
    Input("choice-list", "n_clicks"),
    Input("choice-chart", "n_clicks"),
    Input("type-force", "n_clicks"),
    Input("type-speed", "n_clicks"),
    Input("type-power", "n_clicks"),
    Input("session-metrics", "data"),
    State("session-display-type", "data"),
)
def display_session(l, c, f, s, p, data, display_type):
    if data is not None:
        if ctx.triggered_id == "choice-list":
            table_data = generate_table_data(data)
            return (no_update, {"display": "none"}, table_data, None, "table")
        if ctx.triggered_id == "choice-chart":
            fig = generate_graph(data[0], "Force moyenne (N)", "Force : %{y:.2f} N ")
            return (fig, None, no_update, {"display": "none"}, "graph")
        if ctx.triggered_id == "type-speed":
            fig = generate_graph(data[2], "Vitesse moyenne (M/S)", None)
            return (fig, None, no_update, {"display": "none"}, "graph")
        if ctx.triggered_id == "type-power":
            fig = generate_graph(data[4], "Puissance (Watts)", None)
            return (fig, None, no_update, {"display": "none"}, "graph")
        else:
            fig = generate_graph(data[0], "Force (N)", "Force : %{y:.2f} N ")
            table_data = generate_table_data(data)
            if display_type == "graph":
                return (fig, None, table_data, {"display": "none"}, "graph")
            else:
                return (fig, {"display": "none"}, table_data, None, "table")
    else:
        return (go.Figure(), no_update, no_update, no_update, no_update) """


""" @callback(
    Output("units-buttons", "style"),
    Input("choice-list", "n_clicks"),
    Input("choice-chart", "n_clicks"),
)
def units_buttons(list, chart):
    if ctx.triggered_id == "choice-list":
        return {"display": "none"}
    else:
        return None """
