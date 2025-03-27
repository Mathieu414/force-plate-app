import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, no_update, ctx
import threading
import time
import nidaqmx
import numpy as np
from dash.exceptions import PreventUpdate
from utils.nidaq import sampling_rate, channels, FreeDataAcquisition
from components import FreePageInfoModal, ValueCard, Sliders
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
import plotly.graph_objects as go
import pandas as pd

intervals_frequency = 1000
# default maximum interval time, in ms
max_intervals = 1000 * 60

daq = FreeDataAcquisition(channels)

# TODO : add fz_range integration

dash.register_page(__name__, path="/free-session")

# Define the layout for the new page
layout = html.Div(
    children=[
        # alert div to display informations on the screen
        html.Div(
            id="free-alert-div",
            style={
                "position": "fixed",
                "top": 2,
                "zIndex": "999",
                "left": "50%",
                "transform": "translate(-50%, 0)",
            },
        ),
        dbc.Row(
            [
                dbc.Col(
                    Sliders,
                ),
                dbc.Col(
                    dbc.Button(
                        "Start",
                        id="free-start",
                        color="success",
                        size="lg",
                        style={"fontSize": "18px"},
                    ),
                    width="2",
                    class_name="justify-end",
                ),
                dbc.Col(
                    dbc.Button(
                        "Stop",
                        id="free-stop",
                        color="danger",
                        size="lg",
                        style={"fontSize": "18px"},
                    ),
                    width="3",
                ),
                dbc.Col(
                    dbc.Button(
                        html.I(className="fa fa-question fa-xl"),
                        color="light",
                        id="open-info-modal",
                    ),
                    width=3,
                    class_name="justify-end",
                ),
            ],
            class_name="mb-2",
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div(
                                    id="free-daq-div",
                                    style={"height": "55vh"},
                                ),
                                dbc.Button(
                                    "Reset",
                                    id="free-reset",
                                    color="danger",
                                ),
                            ]
                        ),
                        style={"height": "65vh"},
                    ),
                    width=9,
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            ValueCard(
                                0,
                                "N",
                                "Force Maximale",
                                "free-max-force-card",
                                height=50,
                            ),
                            class_name="mb-2",
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Button(
                                    "Export des données",
                                    id="download-data",
                                    color="primary",
                                ),
                            ),
                            align="center",
                            style={"height": "15vh"},
                        ),
                    ]
                ),
            ],
            class_name="mb-2 mt-4",
            justify="center",
        ),
        dbc.Row(
            [
                # Add Mean Force Value Card
                dbc.Col(
                    ValueCard(
                        0,
                        "N",
                        "Force Moyenne (sélection)",
                        "free-mean-force-card",
                        height=50,
                    ),
                    class_name="mb-2",
                ),
                # Add Selected Force Value Card
                dbc.Col(
                    ValueCard(
                        0,
                        "N",
                        "Force Max (sélection)",
                        "free-selected-force-card",
                        height=50,
                    ),
                    class_name="mb-2",
                ),
            ],
        ),
        dcc.Download(id="download-data-csv"),
        # Max interval value of 1 min
        dcc.Interval(
            id="test-interval-component",
            interval=intervals_frequency,
            n_intervals=0,
            max_intervals=max_intervals,
            disabled=True,
        ),
        FreePageInfoModal,
    ],
)


@callback(
    Output("free-alert-div", "children"),
    Output("test-interval-component", "disabled"),
    Input("free-start", "n_clicks"),
    Input("free-stop", "n_clicks"),
    State("fz-range", "data"),
    prevent_initial_call=True,
)
def control_acquisition(start_clicks, stop_clicks, fz_range):

    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "free-start":
        print("acquisition started")
        if daq.acquisition_thread is None or not daq.acquisition_thread.is_alive():
            daq.start_acquisition()
            return (
                dbc.Alert(
                    "Acquisition lancée",
                    color="success",
                    dismissable=True,
                    style={"margin-bottom": "0"},
                ),
                False,
            )

    elif button_id == "free-stop":
        if daq.stop_acquisition():
            return (
                dbc.Alert(
                    "Acquistion stoppée",
                    color="danger",
                    dismissable=True,
                    style={"margin-bottom": "0"},
                ),
                True,
            )

    raise PreventUpdate


# sets acquisition_running to false if the n_intervals of the interval component is greater than max_intervals
@callback(
    Output("free-alert-div", "children", allow_duplicate=True),
    Input("test-interval-component", "n_intervals"),
    prevent_initial_call=True,
)
def check_timeout(n_intervals):
    # global acquisition_running

    if n_intervals > max_intervals:
        daq.acquisition_running = False
        return dbc.Alert(
            "Timeout",
            color="danger",
            dismissable=True,
            style={"margin-bottom": "0"},
        )

    raise PreventUpdate


@callback(
    Output("free-daq-div", "children"),
    Input("test-interval-component", "disabled"),
    Input("test-interval-component", "n_intervals"),
    Input("free-reset", "n_clicks"),
)
def update_chart(_, n_intervals, n_clicks):
    if ctx.triggered_id == "free-reset":
        figure = go.Figure().update_layout(
            title="Data",
            margin=dict(l=10, r=10, t=30, b=20),
            clickmode="event+select",
        )
        return dcc.Graph(figure=figure, style={"height": "100%"}, id="free-daq-chart")
    if ctx.triggered_id == "test-interval-component":
        sum_data = daq.get_z_data_converted()
        print(sum_data)

        x = list(range(len(sum_data)))
        # Process the data and create the figure
        figure = go.Figure().add_trace(
            go.Scatter(
                x=x,
                y=sum_data,
                mode="lines+markers",
                name=("Vertical force (N)"),
            )
        )
        # Define the zoom range for the last 1000 points
        start_index = len(x) - (1000 if len(x) > 1000 else len(x))
        x_start = x[start_index]
        x_end = x[-1]
        figure.update_layout(
            xaxis=dict(range=[x_start, x_end]),
            title="Data",
            margin=dict(l=10, r=10, t=30, b=20),
        ),

        figure.update_layout(
            clickmode="event+select",
        )
        figure.update_traces(marker_size=1)

        return dcc.Graph(
            figure=figure,
            style={"height": "100%"},
            id="free-daq-chart",
            config={
                "displayModeBar": True,
                "modeBarButtons": [
                    ["zoom2d"],
                    ["zoomIn2d"],
                    ["zoomOut2d"],
                    ["autoScale2d"],
                    ["select2d"],
                    ["toImage"],
                ],
            },
        )
    else:
        return html.H4("Pas encore de données", style={"textAlign": "center"})


@callback(
    Output("free-reset", "style"),
    Input("free-daq-div", "children"),
)
def toggle_reset_button(children):
    if not children["type"] == "Graph":
        return {"display": "none"}
    return {"display": "block"}


@callback(
    Output("free-max-force-card", "children"),
    Input("test-interval-component", "n_intervals"),
    prevent_initial_call=True,
)
def update_max_force(n_intervals):

    return round(daq.max_force, 2)


@callback(
    Output("free-alert-div", "children", allow_duplicate=True),
    Input("free-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_data(n_clicks):

    daq.global_data_z = np.empty((4, 1))
    daq.max_force = 0

    return dbc.Alert(
        "Données réinitialisées",
        color="danger",
        dismissable=True,
        style={"margin-bottom": "0"},
    )


@callback(
    Output("download-data-csv", "data"),
    Input("download-data", "n_clicks"),
    prevent_initial_call=True,
)
def download_data(n_clicks):

    pdf = pd.DataFrame(daq.global_data_z.T, columns=["Fz1", "Fz2", "Fz3", "Fz4"])

    return dcc.send_data_frame(pdf.to_csv, "data.csv")


# New callback to handle selection on the graph and update the force cards
@callback(
    Output("free-mean-force-card", "children"),
    Output("free-selected-force-card", "children"),
    Input("free-daq-chart", "selectedData"),
    prevent_initial_call=True,
)
def update_selection_stats(selection_data):
    print(selection_data)
    if (
        not selection_data
        or "points" not in selection_data
        or not selection_data["points"]
    ):
        raise PreventUpdate

    # Extract y values from the selected points
    selected_y_values = [point["y"] for point in selection_data["points"]]

    # Calculate mean force from selection
    mean_force = np.mean(selected_y_values) if selected_y_values else 0

    # Get the current value at the last selected point
    selected_force = selected_y_values[-1] if selected_y_values else 0

    return round(mean_force, 2), round(selected_force, 2)
