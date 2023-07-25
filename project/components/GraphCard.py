import pandas as pd
from dash import html, dcc
import pandas as pd
from dash import Input, Output, State, callback, ctx, no_update
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
from nidaqmx.constants import TerminalConfiguration, READ_ALL_AVAILABLE, AcquisitionType
from utils.utils import substract_arrays
import time
import threading
import scipy.integrate as it

import plotly.express as px

controller = False


GraphCard = dbc.Card(
    children=[
        html.H4("Courbe du mouvement", className="ms-2 mt-2"),
        dcc.Graph(
            id="daq-chart",
            className="h-100",
            figure=go.Figure().update_layout(
                margin=dict(l=10, r=10, t=10, b=20),
            ),
        ),
    ],
    style={"height": "38vh"},
)


@callback(
    Output("daq-chart", "figure"),
    Output("complete-graph", "figure"),
    Output("force-card-text", "children"),
    Output("velocity-card-text", "children"),
    Output("max-speed-card-text", "children"),
    Output("power-card-text", "children"),
    Output("profile-data", "data"),
    Input("start", "n_clicks"),
    Input("profile-reset-button", "n_clicks"),
    Input("datatable-fvp", "derived_virtual_data"),
    State("weight-data", "data"),
    State("profile-data", "data"),
    State("load-input", "value"),
    prevent_initial_call=True,
)
def data_acquisition_start(start, n, rows, weight, stored_profile, load):
    if ctx.triggered_id == "start":
        print("start acquisition")

        data, global_data = nidaq_trigger(weight, load)

        num_samples = len(data[0])

        time = np.linspace(0, num_samples / sampling_rate, num_samples)
        global_time = np.linspace(
            0, len(global_data[0]) / sampling_rate, len(global_data[0])
        )
        # Create traces
        fig = go.Figure()
        global_fig = go.Figure()

        # compute the force and velocity values
        sum_newton = np.sum(np.array(data)[4:8], axis=0) / 0.0018
        global_sum = np.sum(np.array(global_data)[4:8], axis=0) / 0.0018

        # force is very straight-forward
        mean_newton = np.mean(sum_newton)
        # we integrate the force to find the velocity
        if load is None:
            load = 0

        acceleration = (sum_newton / (weight + load)) - 9.80665

        velocity = it.cumulative_trapezoid(acceleration, time, initial=0)
        fig.add_trace(
            go.Scatter(x=time, y=sum_newton, mode="lines", name=("Vertical force (N)"))
        )
        for i in global_data:
            global_fig.add_trace(
                go.Scatter(
                    x=global_time,
                    y=i,
                    mode="lines",
                    name=("Vertical force (N)"),
                )
            )
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=20),
            xaxis_title="Temps (s)",
            yaxis_title="Force (N)",
        )
        global_fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=20),
            xaxis_title="Temps (s)",
            yaxis_title="Force (N)",
        )

        mean_velocity = np.mean(velocity)

        if stored_profile is None:
            stored_profile = [
                [mean_newton],
                [mean_velocity],
                [load],
            ]
        else:
            stored_profile[0].append(mean_newton)
            stored_profile[1].append(mean_velocity)
            stored_profile[2].append(load)

        power = sum_newton * velocity

        mean_power = np.mean(power)

        return (
            fig,
            global_fig,
            round(mean_newton),
            round(mean_velocity, 2),
            round(velocity[-1], 2),
            round(mean_power),
            stored_profile,
        )
    if ctx.triggered_id == "profile-reset-button":
        return no_update, no_update, no_update, no_update, no_update, no_update, None

    if ctx.triggered_id == "datatable-fvp":
        print("data_table_interactivity")
        if stored_profile is not None:
            if rows != []:
                df = pd.DataFrame(rows)
                stored_profile = [
                    df["Force (N)"].values.tolist(),
                    df["Vitesse (m/s)"].values.tolist(),
                    df["Poids (kg)"].values.tolist(),
                ]
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                stored_profile,
            )
        else:
            raise PreventUpdate


@callback(
    Output("daq-chart", "style"),
    Input("end", "n_clicks"),
    prevent_initial_call=True,
)
def data_acquisition_end(n_clicks):
    print("end button triggered\n")
    # not sure if it is the right way to proceed though
    global controller
    controller = True


def nidaq_start_stop():
    samples = [[] for x in range(8)]
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(
            ",".join(channels), terminal_config=TerminalConfiguration.DIFF
        )

        task.timing.cfg_samp_clk_timing(1000, sample_mode=AcquisitionType.CONTINUOUS)

        def sample_callback(
            task_handle, every_n_samples_event_type, number_of_samples, callback_data
        ):
            """Callback function for reading singals."""
            print("Every N Samples callback invoked.")

            new_data = task.read(number_of_samples_per_channel=1000)

            for i, v in enumerate(samples):
                samples[i].extend(new_data[i])

            return 0

        task.register_every_n_samples_acquired_into_buffer_event(1000, sample_callback)

        task.start()

        # timeout a bit more than 10s, otherwise there is conflict with the callback if the timeout
        # falls exactly on a second (for example 10s)
        timeout = time.time() + 10.5

        global controller

        while True:
            if controller or time.time() > timeout:
                controller = False
                break

    return samples


def nidaq_trigger(weight, load):
    if load is None:
        load = 0

    samples = [[] for x in range(8)]
    global_samples = [[] for x in range(8)]
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(
            ",".join(channels), terminal_config=TerminalConfiguration.DIFF
        )

        task.timing.cfg_samp_clk_timing(1000, sample_mode=AcquisitionType.CONTINUOUS)

        global trigger_control
        global measurement_end

        trigger_control = False
        measurement_end = False

        def sample_callback(
            task_handle, every_n_samples_event_type, number_of_samples, callback_data
        ):
            """Callback function for reading singals."""
            print("Every N Samples callback invoked.")

            new_data = np.array(task.read(number_of_samples_per_channel=1000))

            for i, v in enumerate(global_samples):
                global_samples[i].extend(new_data[i])

            new_data_z = np.sum(new_data[-4:], axis=0)

            # Define the threshold
            above_threshold = new_data_z > ((weight + load) * 0.0018 * 9.80665 + 0.05)
            under_threshold = new_data_z < ((weight + load) * 0.0018 * 9.80665)

            global trigger_control
            global measurement_end

            first_index = 0

            last_index = -1

            for i in range(len(new_data_z) - 19):
                next_above_threshold = np.all(above_threshold[i : i + 20])
                next_under_threshold = np.all(under_threshold[i : i + 20])
                # if the trigger is off and the threshold is detected
                if not trigger_control and next_above_threshold and not measurement_end:
                    first_index = i - 10 if i - 10 >= 0 else 0
                    print("trigger on")
                    trigger_control = True
                # if the trigger is on and the data goes under the threshold
                if trigger_control and next_under_threshold and not measurement_end:
                    last_index = i
                    print("trigger off")
                    print(first_index)
                    print(last_index)
                    for j, v in enumerate(samples):
                        samples[j].extend(new_data[j][first_index:last_index])
                    trigger_control = False
                    measurement_end = True

            # case if the trigger stays on at the end of the buffer reading
            if trigger_control:
                for i, v in enumerate(samples):
                    samples[i].extend(new_data[i][first_index:last_index])
                trigger_control = False

            return 0

        task.register_every_n_samples_acquired_into_buffer_event(1000, sample_callback)

        task.start()

        # timeout a bit more than 10s, otherwise there is conflict with the callback if the timeout
        # falls exactly on a second (for example 10s)
        timeout = time.time() + 5.5

        while True:
            # check if either the timeout is reached or the samples have been recorded but the trigger is now off
            if time.time() > timeout or measurement_end:
                break

    return samples, global_samples
