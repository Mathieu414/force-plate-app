import dash
from dash import html, Output, Input, callback, ctx, dcc
import nidaqmx
from utils.nidaq import nidaq_base_config
import dash_bootstrap_components as dbc
from components import ValueCard, GraphCard, StartStopCalibrate, Sliders, WeightCard
import plotly.graph_objects as go
import plotly.express as px
from dash.exceptions import PreventUpdate


dash.register_page(__name__)

layout = html.Div(
    [
        Sliders,
        dbc.Row(
            [
                dbc.Col(html.H2("Test Profil Force/Vitesse"), align="center"),
                dbc.Col(StartStopCalibrate, align="center", className="text-center"),
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
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Col(WeightCard, width=3),
                dbc.Col(GraphCard, align="center"),
            ],
            className="mb-2",
            align="center",
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    width=3,
                    children=[
                        dbc.Card(
                            className="text-center",
                            children=dbc.CardBody(
                                children=[
                                    html.H3(
                                        className="mb-1 mt-2 card-title",
                                        style={"font-size": "4.2vw"},
                                        children=0,
                                        id="velocity-card-text",
                                    ),
                                    html.H2(
                                        className="card-title mb-1",
                                        children="m/s",
                                        style={"font-size": "2vw"},
                                    ),
                                    html.Small(
                                        className="card-text",
                                        children="Vitesse",
                                    ),
                                ],
                                className="my-auto",
                                style={"flex": 0},
                            ),
                            style={"height": "30vh"},
                        )
                    ],
                ),
                dbc.Col(
                    width={"size": 3},
                    children=[
                        dbc.Card(
                            className="text-center",
                            children=dbc.CardBody(
                                children=[
                                    html.H3(
                                        className="mb-1 mt-2 card-title",
                                        style={"font-size": "4.2vw"},
                                        children=0,
                                        id="force-card-text",
                                    ),
                                    html.H2(
                                        className="card-title mb-1",
                                        children="N",
                                        style={"font-size": "2vw"},
                                    ),
                                    html.Small(
                                        className="card-text",
                                        children="Force",
                                    ),
                                ],
                                className="my-auto",
                                style={"flex": 0},
                            ),
                            style={"height": "30vh"},
                        )
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
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Col(
                    width={"size": 3},
                    children=[
                        dbc.Card(
                            className="text-center",
                            children=dbc.CardBody(
                                children=[
                                    html.H3(
                                        className="mb-1 mt-2 card-title",
                                        style={"font-size": "4.2vw"},
                                        children=0,
                                        id="max-speed-card-text",
                                    ),
                                    html.H2(
                                        className="card-title mb-1",
                                        children="m/s",
                                        style={"font-size": "2vw"},
                                    ),
                                    html.Small(
                                        className="card-text",
                                        children="Vitesse max",
                                    ),
                                ],
                                className="my-auto",
                                style={"flex": 0},
                            ),
                            style={"height": "30vh"},
                        )
                    ],
                ),
                dbc.Col(
                    width={"size": 3},
                    children=[
                        dbc.Card(
                            className="text-center",
                            children=dbc.CardBody(
                                children=[
                                    html.H3(
                                        className="mb-1 mt-2 card-title",
                                        style={"font-size": "4.2vw"},
                                        children=0,
                                        id="power-card-text",
                                    ),
                                    html.H2(
                                        className="card-title mb-1",
                                        children="Watt",
                                        style={"font-size": "2vw"},
                                    ),
                                    html.Small(
                                        className="card-text",
                                        children="Puissance",
                                    ),
                                ],
                                className="my-auto",
                                style={"flex": 0},
                            ),
                            style={"height": "30vh"},
                        )
                    ],
                ),
            ]
        ),
        dcc.Store(id="weight-data", storage_type="session"),
        dcc.Store(id="profile-data", storage_type="session"),
    ]
)


@callback(Output("profile-chart", "figure"), Input("profile-data", "data"))
def update_profile_chart(data):
    print("update chart")
    print(data)
    if data is not None:
        figure = px.scatter(x=data[1], y=data[0])
        figure.update_layout(
            margin=dict(l=10, r=10, t=10, b=20),
            yaxis_title="Force",
            xaxis_title="Vitesse",
        )
        return figure
    else:
        return go.Figure().update_layout(
            margin=dict(l=10, r=10, t=10, b=20),
            xaxis_title="Force",
            yaxis_title="Vitesse",
        )
