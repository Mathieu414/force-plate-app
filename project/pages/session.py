import pandas as pd
import dash
import pandas as pd
from dash import Input, Output, State, callback, ctx, no_update, html, dcc, dash_table
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
    SessionDataAcquisition,
)
from utils.utils import analyse_jump, convert_voltage_to_force
import asyncio
from components import (
    ParametersModal,
    SessionPageInfoModal,
    LiveTabContent,
    SummaryTabContent,
    DetailsTabContent,
    WeightingModal,
    GoModal,
)
import plotly.express as px

daq = SessionDataAcquisition(channels)

dash.register_page(__name__, path="/seance")

total_movement_tab_content = dbc.Row(
    children=[
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    children=[
                        html.H4("Mouvement total"),
                        dcc.Graph(
                            id="session-global-chart",
                            style={"height": "50vh"},
                            figure=go.Figure().update_layout(
                                margin=dict(l=10, r=10, t=10, b=20),
                            ),
                        ),
                    ],
                ),
                style={"height": "60vh"},
            ),
        ),
    ],
    class_name="mt-2",
)


layout = html.Div(
    [
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dbc.Button(
                            html.I(className="fa fa-gear fa-xl"),
                            color="light",
                            id="open-parameters-modal",
                        ),
                        dbc.Tooltip(
                            "Paramètres",
                            target="open-parameters-modal",
                            placement="bottom",
                        ),
                        html.Span(
                            [dbc.Spinner(size="sm"), " Pesée en cours"],
                            style={"display": "none"},
                            id="weight-spinner",
                        ),
                    ],
                    width=5,
                ),
                dbc.Col(
                    dbc.Row(
                        dbc.Button(
                            id="session-start",
                            children="Start",
                            color="success",
                            style={"fontSize": "18px"},
                        ),
                        justify="center",
                    ),
                    id="session-start-div",
                    width=2,
                ),
                dbc.Col(
                    dbc.Row(
                        dbc.Button(
                            id="session-stop",
                            children="Stop",
                            color="danger",
                            style={"fontSize": "18px"},
                        ),
                        justify="center",
                    ),
                    id="session-stop-div",
                    style={"display": "none"},
                    width=2,
                ),
                dbc.Col(
                    children=[
                        dbc.Button(
                            html.I(className="fa fa-trash-can fa-xl"),
                            id="reset-session",
                            color="light",
                            className="me-2",
                        ),
                        dbc.Tooltip(
                            "Réinitialisation de la séance",
                            target="reset-session",
                            placement="bottom",
                        ),
                        dbc.Button(
                            html.I(className="fa fa-refresh fa-xl"),
                            id="reset-weight",
                            color="light",
                            className="me-2",
                        ),
                        dbc.Tooltip(
                            "Réinitialisation du poids",
                            target="reset-weight",
                            placement="bottom",
                        ),
                        html.Div(
                            [html.Span("Poids : "), html.Span(id="weight-span")],
                            className="m-3",
                        ),
                        dbc.Button(
                            html.I(className="fa fa-question fa-xl"),
                            color="light",
                            id="open-info-modal",
                        ),
                        dbc.Tooltip(
                            "Aide",
                            target="open-info-modal",
                            placement="bottom",
                        ),
                    ],
                    width=5,
                    class_name="justify-end",
                ),
            ],
            justify="between",
            class_name="mb-2",
        ),
        # alert div to display informations on the screen
        html.Div(
            id="session-updater-alert-div",
            style={
                "position": "fixed",
                "top": 2,
                "zIndex": "999",
                "left": "50%",
                "transform": "translate(-50%, 0)",
            },
        ),
        html.Div(
            id="session-loop-alert-div",
            style={
                "position": "fixed",
                "top": 10,
                "zIndex": "999",
                "left": "50%",
                "transform": "translate(-50%, 0)",
            },
        ),
        SessionPageInfoModal,
        WeightingModal,
        ParametersModal(daq=daq),
        GoModal,
        dbc.Tabs(
            [
                dbc.Tab(LiveTabContent, label="Live"),
                dbc.Tab(SummaryTabContent, label="Summary"),
                dbc.Tab(DetailsTabContent, label="Details"),
                # dbc.Tab(MetricsTabContent, label="Metrics"),
                # dbc.Tab(MainTabContent, label="Mouvement"),
                dbc.Tab(total_movement_tab_content, label="Mouvement Total"),
            ]
        ),
        dbc.Button(id="weight-trigger", style={"display": "none"}),
        dcc.Interval(
            id="session-interval-component",
            interval=1000,
            n_intervals=0,
            disabled=True,
        ),
        dcc.Interval(
            id="session-weight-interval-component",
            interval=1000,
            n_intervals=0,
            disabled=True,
        ),
        dcc.Store(id="session-metrics", storage_type="session"),
        dcc.Store(id="session-jumps", storage_type="session"),
        dcc.Store(id="session-full-data", storage_type="session"),
        dcc.Store(id="weight-data", storage_type="session"),
        # component to store if the session-display is displaying a graph or a table
        dcc.Store(id="session-display-type", storage_type="session", data="graph"),
    ]
)


@callback(
    Output("reset-session", "style"),
    Input("session-stop", "n_clicks"),
)
def stop_daq(stop):
    daq.stop_acquisition()


@callback(
    Output("weight-trigger", "n_clicks"),
    Input("session-weight-interval-component", "n_intervals"),
    prevent_initial_call=True,
)
def listen_weight(n_weight):
    if daq.weight is not None:
        return 1
    else:
        raise PreventUpdate


@callback(
    Output("session-stop-div", "style"),
    Output("weighting-modal", "is_open"),
    Output("session-start-div", "style"),
    Output("session-weight-interval-component", "disabled"),
    Output("session-interval-component", "disabled"),
    Output("weight-data", "data"),
    Output("session-loop-alert-div", "children"),
    Output("weight-spinner", "style"),
    Input("session-stop", "n_clicks"),
    Input("session-start", "n_clicks"),
    Input("reset-session", "n_clicks"),
    Input("reset-weight", "n_clicks"),
    Input("weight-trigger", "n_clicks"),
    State("weighting-modal", "is_open"),
    State("weight-data", "data"),
    prevent_initial_call=True,
)
def start_stop_handling(
    stop, start, reset_session, reset_weight, n_weight, is_disabled, weight_data
):
    if ctx.triggered_id == "session-stop":
        return (
            {"display": "none"},
            False,
            None,
            True,
            True,
            no_update,
            no_update,
            {"display": "none"},
        )
    if ctx.triggered_id == "session-start":
        daq.start_acquisition()
        return (
            None,
            True,
            {"display": "none"},
            False,
            no_update,
            no_update,
            no_update,
            None,
        )
    if ctx.triggered_id == "weight-trigger":
        alert_message = dbc.Alert(
            children=[
                html.I(className="fa fa-check"),
                " Vous pouvez commencer la séance",
            ],
            color="success",
            dismissable=True,
            duration=3000,
        )
        return (
            no_update,
            False,
            no_update,
            True,
            False,
            daq.weight,
            alert_message,
            {"display": "none"},
        )
    if ctx.triggered_id == "reset-session":
        return (
            no_update,
            no_update,
            no_update,
            True,  # Disable weight interval
            True,  # Disable session interval
            None,  # Reset weight data
            dbc.Alert(
                "Données réinitialisées",
                color="warning",
                dismissable=True,
                duration=3000,
            ),
            {"display": "none"},
        )
    if ctx.triggered_id == "reset-weight":
        daq.stop_acquisition()
        daq.weight = None
        return (
            no_update,
            no_update,
            no_update,
            True,  # Disable weight interval
            True,  # Disable session interval
            None,  # Reset weight data
            dbc.Alert(
                "Poids réinitialisé",
                color="warning",
                dismissable=True,
                duration=3000,
            ),
            {"display": "none"},
        )


@callback(
    Output("weight-span", "children"),
    Input("weight-data", "data"),
)
def display_weight(weight_data):
    if weight_data:
        return f"{weight_data:.2f}"
    else:
        return "Pas de poids mesuré"


@callback(
    Output("session-global-chart", "figure"),
    Output("session-full-data", "data"),
    Input("session-stop", "n_clicks"),
    State("fz-range", "data"),
    State("session-full-data", "data"),
)
def update_global_chart(_, fz_range, full_data):
    data_z = daq.get_data_z()

    if data_z.shape[1] == 1:
        if full_data is None:
            raise PreventUpdate
        data_z = np.array(full_data)

    jumps_data = daq.get_jumps_data()

    coef = 1 / (0.0018 / (float(fz_range) / 2.5))

    # Get individual channel data and multiply by coefficient
    data_channels = [data_z[i] * coef for i in range(len(data_z))]
    sum_data = np.sum(data_z, axis=0) * coef

    # Create figure
    figure = go.Figure()

    # Add trace for each channel
    for idx, channel_data in enumerate(data_channels):
        x = list(range(len(channel_data)))
        figure.add_trace(
            go.Scatter(
                x=x,
                y=channel_data,
                mode="lines",
                name=f"Channel {idx+1}",
                line=dict(width=3),
            )
        )

    x = list(range(len(sum_data)))

    # Add trace for sum of all channels
    figure.add_trace(
        go.Scatter(
            x=x, y=sum_data, mode="lines", name="Total Force", line=dict(width=3)
        )
    )

    figure.update_layout(
        title="Force Plate Data by Channel",
        margin=dict(l=10, r=10, t=30, b=20),
        xaxis_title="Sample",
        yaxis_title="Force (N)",
    )

    # Add jumps data traces if available
    if jumps_data:
        # Plot peak points
        figure.add_trace(
            go.Scatter(
                x=jumps_data[0],  # peaks
                y=[sum_data[p] for p in jumps_data[0]],
                mode="markers",
                name="Peaks",
                marker=dict(symbol="x", size=10, color="blue"),
            )
        )

        # Plot vertical prominence lines
        for idx, peak in enumerate(jumps_data[0]):
            figure.add_trace(
                go.Scatter(
                    x=[peak, peak],
                    y=[
                        sum_data[peak] - (jumps_data[1][idx]["prominences"][0] * coef),
                        sum_data[peak],
                    ],
                    mode="lines",
                    name="Prominence",
                    line=dict(color="orange"),
                    showlegend=(idx == 0),
                )
            )

        # Plot horizontal width lines
        for i, jump_data in enumerate(jumps_data[1]):
            figure.add_trace(
                go.Scatter(
                    x=[jump_data["left_ips"], jump_data["right_ips"]],
                    y=[
                        jump_data["width_heights"] * coef,
                        jump_data["width_heights"] * coef,
                    ],
                    mode="lines",
                    name="Width",
                    line=dict(color="orange"),
                    showlegend=(i == 0),
                )
            )
            # Add scatter points at the endpoints
            figure.add_trace(
                go.Scatter(
                    x=[jump_data["left_ips"], jump_data["right_ips"]],
                    y=[
                        jump_data["width_heights"] * coef,
                        jump_data["width_heights"] * coef,
                    ],
                    mode="markers",
                    name="Width points",
                    marker=dict(color="orange", size=8),
                    showlegend=(i == 0),
                )
            )

    return figure, data_z


# TODO : update session-metrics when stop button is pressed


@callback(
    Output("session-metrics", "data"),
    Output("session-jumps", "data"),
    Output("session-updater-alert-div", "children"),
    Input("session-interval-component", "n_intervals"),
    Input("reset-session", "n_clicks"),
    State("weight-data", "data"),
    State("session-metrics", "data"),
    State("fz-range", "data"),
    prevent_initial_call=True,
)
def interval_updater(n, reset_session, weight, stored_data, fz_range):
    global daq
    if ctx.triggered_id == "reset-session":
        daq = SessionDataAcquisition(channels)
        return (None, None, no_update)
    if weight is None:
        alert_message = dbc.Alert(
            "Pas de données de poids",
            color="danger",
            dismissable=True,
        )
        return (
            no_update,
            no_update,
            alert_message,
        )
    data_x = daq.get_data_x()
    data_y = daq.get_data_y()
    data_z = daq.get_data_z()
    sum_data = np.sum(data_z, axis=0)

    jumps_data = daq.get_jumps_data()

    if jumps_data is None:
        raise PreventUpdate

    peaks = jumps_data[0]
    properties = jumps_data[1]

    jumps_curves = []
    mean_forces = []
    max_forces = []
    mean_velocities = []
    max_velocities = []
    mean_powers = []
    max_powers = []
    rate_of_force_developments = []
    max_rfds = []
    jump_heights = []
    gcts = []
    rsis = []
    for peak in peaks:
        peak

        buffer_coef = 0.02

        # Find points below threshold after the last wide peak
        after_peak = np.where(sum_data[peak:] < daq.threshold * (1 - buffer_coef))[0]
        if len(after_peak) == 0:
            raise PreventUpdate
        after_point = after_peak[1] + peak

        # Find points below threshold before the last wide peak
        before_peak = np.where(sum_data[:peak] < daq.threshold * (1 + buffer_coef))[0]
        if len(before_peak) == 0:
            raise PreventUpdate
        before_point = before_peak[-2]

        # Extract peak data between these points
        peak_data_x = data_x[:, before_point:after_point]
        peak_data_y = data_y[:, before_point:after_point]
        peak_data_z = data_z[:, before_point:after_point]

        peak_data_force = np.array(
            [convert_voltage_to_force(col, daq.fz_range) for col in peak_data_z]
        )

        sum_peak_data = np.sum(peak_data_z, axis=0)

        # TODO : this should go in the nidaq class
        metrics = analyse_jump(
            data=sum_peak_data,
            weight=weight,
            load=0,
            fz_range=fz_range,
            sampling_rate=daq.sample_frequency,
        )
        mean_forces.append(metrics["mean_force"])
        max_forces.append(np.max(metrics["force"]))
        mean_velocities.append(metrics["mean_velocity"])
        max_velocities.append(np.max(metrics["velocity"]))
        mean_powers.append(metrics["mean_power"])
        max_powers.append(np.max(metrics["power"]))
        rate_of_force_developments.append(np.mean(metrics["rate_of_force_development"]))
        max_rfds.append(metrics["max_rfd"])
        jump_heights.append(metrics["jump_height"])
        gcts.append(metrics["gct"])
        rsis.append(metrics["rsi"])
        jumps_curves.append(
            [
                metrics["time"],
                metrics["force"],
                metrics["velocity"],
                [peak_data_x, peak_data_y, peak_data_z],
            ]
        )

    stored_data = np.array(
        [
            mean_forces,
            max_forces,
            mean_velocities,
            max_velocities,
            mean_powers,
            max_powers,
            rate_of_force_developments,
            max_rfds,
            jump_heights,
            gcts,
            rsis,
        ]
    )

    return (
        stored_data,
        jumps_curves,
        no_update,
    )
