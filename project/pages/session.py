import pandas as pd
import dash
import pandas as pd
from dash import Input, Output, State, callback, ctx, no_update, html, dcc
from dash.exceptions import PreventUpdate
import nidaqmx
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc
from utils.nidaq import (
    nidaq_base_config,
    sampling_rate,
    num_samples,
    channels,
)
from components import Sliders, StartStopCalibrate, WeightCard, ValueCard
from components.GraphCard import nidaq_trigger

is_recording = False

dash.register_page(__name__, path="/seance")

layout = html.Div(
    [
        Sliders,
        html.H2("Séance", className="text-center"),
        dbc.Row(
            [
                dbc.Col(WeightCard(35), width=4),
                dbc.Col(
                    children=[
                        dbc.Card(
                            dbc.CardBody(
                                children=[
                                    html.H4("Mouvement"),
                                    dcc.Graph(
                                        id="session-chart",
                                        style={"height": "25vh"},
                                        figure=go.Figure().update_layout(
                                            margin=dict(l=10, r=10, t=10, b=20),
                                        ),
                                    ),
                                ],
                            ),
                            style={"height": "35vh"},
                        ),
                    ],
                    width=8,
                ),
            ],
            class_name="mb-2",
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.Div(
                            children=[
                                dbc.Button(
                                    id="session-start",
                                    children="Démarrer",
                                    color="success",
                                    size="lg",
                                    style={"font-size": "18px"},
                                    class_name="me-3",
                                ),
                                dbc.Button(
                                    id="session-stop",
                                    children="Arrêter",
                                    color="danger",
                                    size="lg",
                                    style={"font-size": "18px"},
                                ),
                            ],
                            className="my-5",
                        ),
                    ],
                    align="center",
                    class_name="text-center",
                    width=4,
                ),
                dbc.Col(ValueCard(0, "N", "Force", "session-power-card", height=25)),
                dbc.Col(
                    ValueCard(0, "m/s", "Vitesse", "session-speed-card", height=25)
                ),
                dbc.Col(
                    ValueCard(0, "watt", "Puissance", "session-power-card", height=25)
                ),
            ],
            class_name="mb-2",
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Input(
                        placeholder="Charge supplémentaire (kg)",
                        size="lg",
                        type="number",
                        min=0,
                        id="load-input-session",
                    ),
                    align="center",
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
                                                ),
                                                dbc.Button(
                                                    html.I(
                                                        className="fas fa-chart-line"
                                                    ),
                                                ),
                                            ]
                                        ),
                                        dbc.Col(
                                            children=[
                                                dbc.Button("N"),
                                                dbc.Button("M/S"),
                                                dbc.Button("Watt"),
                                            ],
                                            class_name="text-end",
                                        ),
                                    ],
                                    justify="between",
                                ),
                                dcc.Graph(),
                            ]
                        )
                    ),
                    width=8,
                ),
            ]
        ),
        dcc.Interval(
            id="interval-component", interval=1 * 500, n_intervals=0, disabled=True
        ),
    ]
)


@callback(
    Output("interval-component", "disabled"),
    Input("session-stop", "n_clicks"),
    Input("session-start", "n_clicks"),
    State("interval-component", "disabled"),
    prevent_initial_call=True,
)
def loop_handling(stop, start, is_disabled):
    return not is_disabled


@callback(
    Output("session-start", "n_clicks"),
    Input("interval-component", "n_intervals"),
    prevent_initial_call=True,
)
def loop_handling(n):
    if not is_recording:
        return 1
    else:
        raise PreventUpdate


@callback(
    Output("session-chart", "figure"),
    Input("interval-component", "n_intervals"),
    prevent_initial_call=True,
)
def session_trigger(n):
    global is_recording
    is_recording = True
    data, _ = nidaq_trigger(90, 0)

    num_samples = len(data[0])

    time = np.linspace(0, num_samples / sampling_rate, num_samples)
    fig = go.Figure()
    sum_newton = np.sum(np.array(data)[4:8], axis=0) / 0.0018
    fig.add_trace(
        go.Scatter(x=time, y=sum_newton, mode="lines", name=("Vertical force (N)"))
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=20),
        xaxis_title="Temps (s)",
        yaxis_title="Force (N)",
    )
    is_recording = False
    print(data)
    if data[0] == []:
        raise PreventUpdate
    else:
        return fig
