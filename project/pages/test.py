import dash
from dash import html, Output, Input, callback, ctx, dcc, dash_table
import nidaqmx
from utils.nidaq import nidaq_base_config
import dash_bootstrap_components as dbc
from components import (
    ValueCard,
    GraphCard,
    StartStopCalibrate,
    Sliders,
    WeightCard,
)
import plotly.graph_objects as go
import plotly.express as px
from dash.exceptions import PreventUpdate
import pandas as pd


dash.register_page(__name__)

layout = html.Div(
    [
        Sliders,
        dbc.Row(
            [
                dbc.Col(html.H2("Test Profil Force/Vitesse"), align="center"),
                dbc.Col(StartStopCalibrate, align="center", class_name="text-center"),
                dbc.Col(
                    dbc.Input(
                        placeholder="Charge supplémentaire (kg)",
                        size="lg",
                        type="number",
                        min=0,
                        id="load-input",
                    ),
                    align="center",
                ),
            ],
            class_name="mb-2",
        ),
        dbc.Row(
            [
                dbc.Col(WeightCard(), width=3),
                dbc.Col(GraphCard, align="center"),
            ],
            class_name="mb-2",
            align="center",
        ),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    children=[
                        html.H4("Courbe Complete", className="ms-2 mt-2"),
                        dcc.Graph(id="complete-graph"),
                    ]
                )
            ),
            class_name="mb-2",
            # style={"display": "none"},
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    width=3,
                    children=[
                        ValueCard(
                            card_value=0,
                            card_description="m/s",
                            card_tail="Vitesse",
                            card_id="velocity-card-text",
                        ),
                    ],
                ),
                dbc.Col(
                    width={"size": 3},
                    children=[
                        ValueCard(0, "N", "Force", "force-card-text"),
                    ],
                ),
                dbc.Col(
                    dbc.Card(
                        children=[
                            html.Div(
                                [
                                    html.H4(
                                        "Profil Force/Vitesse", className="ms-2 mt-2"
                                    ),
                                    dbc.Button(
                                        "Reset",
                                        color="danger",
                                        size="sm",
                                        class_name="m-2",
                                        id="profile-reset-button",
                                    ),
                                ],
                                className="d-grid d-md-flex justify-content-md-between",
                            ),
                            dcc.Graph(
                                id="profile-chart",
                                className="h-100",
                                figure=go.Figure().update_layout(
                                    margin=dict(l=10, r=10, t=10, b=20),
                                ),
                            ),
                        ],
                        style={"height": "30vh"},
                    )
                ),
            ],
            class_name="mb-2",
        ),
        dbc.Row(
            [
                dbc.Col(
                    width={"size": 3},
                    children=[
                        ValueCard(0, "m/s", "Vitesse max", "max-speed-card-text"),
                    ],
                ),
                dbc.Col(
                    width={"size": 3},
                    children=[
                        ValueCard(0, "Watt", "Puissance", "power-card-text"),
                    ],
                ),
                dbc.Col(
                    children=[
                        html.H4("Mesures"),
                        dash_table.DataTable(
                            id="datatable-fvp",
                            editable=True,
                            row_deletable=True,
                            export_format="xlsx",
                        ),
                    ],
                ),
            ],
            justify="center",
        ),
        dcc.Store(id="profile-data", storage_type="session"),
        dcc.Store(id="graph-data", storage_type="session"),
    ]
)


@callback(Output("profile-chart", "figure"), Input("profile-data", "data"))
def update_profile_chart(data):
    print("update chart")
    print(data)
    if data is not None and data != [[], []]:
        figure = px.scatter(x=data[1], y=data[0])
        figure.update_layout(
            margin=dict(l=10, r=10, t=10, b=20),
            yaxis_title="Force",
            xaxis_title="Vitesse",
        )
        figure.update_traces(hovertemplate="Poids : %{text}", text=data[3])
        return figure
    else:
        return go.Figure().update_layout(
            margin=dict(l=10, r=10, t=10, b=20),
            xaxis_title="Force",
            yaxis_title="Vitesse",
        )


@callback(Output("datatable-fvp", "data"), Input("profile-data", "data"))
def set_datatable(profile_data):
    if profile_data is not None:
        df = pd.DataFrame(profile_data).transpose()
        df.columns = ["Force (N)", "Vitesse (m/s)", "Puissance (Watts)", "Poids (kg)"]
        df = df.round(2)
        return df.to_dict("records")
