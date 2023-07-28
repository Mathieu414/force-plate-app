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
    sampling_rate,
    channels,
)
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
from utils.utils import substract_arrays
import time
import scipy.integrate as it

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
    State("fz-range", "data"),
    prevent_initial_call=True,
)
def data_acquisition_start(start, n, rows, weight, stored_profile, load, fz_range):
    if ctx.triggered_id == "start":
        print("start acquisition")

        if load is None:
            load = 0

        data, global_data = nidaq_trigger(weight, load, fz_range)

        if data != []:
            (
                time,
                sum_newton,
                mean_newton,
                velocity,
                mean_velocity,
                mean_power,
            ) = analyse_jump(data, weight, load, fz_range)

            global_time = np.linspace(
                0, len(global_data) / sampling_rate, len(global_data)
            )
            # Create traces
            fig = go.Figure()
            global_fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=time, y=sum_newton, mode="lines", name=("Vertical force (N)")
                )
            )
            global_fig.add_trace(
                go.Scatter(
                    x=global_time,
                    y=np.array(global_data) / (0.0018 / (fz_range / 2.5)),
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

            if stored_profile is None:
                stored_profile = [
                    [mean_newton],
                    [mean_velocity],
                    [mean_power],
                    [load],
                ]
            else:
                stored_profile[0].append(mean_newton)
                stored_profile[1].append(mean_velocity)
                stored_profile[2].append(mean_power)
                stored_profile[3].append(load)

            return (
                fig,
                global_fig,
                round(mean_newton),
                round(mean_velocity, 2),
                round(velocity[-1], 2),
                round(mean_power),
                stored_profile,
            )
        else:
            raise PreventUpdate
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
                    df["Puissance (Watts)"].values.tolist(),
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


def nidaq_trigger(weight, load, fz_range):
    if load is None:
        load = 0

    global samples

    samples = []
    global_samples = []
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(
            ",".join(channels), terminal_config=TerminalConfiguration.DIFF
        )

        task.timing.cfg_samp_clk_timing(1000, sample_mode=AcquisitionType.CONTINUOUS)

        global trigger_control
        global measurement_end
        global last_buffer

        trigger_control = False
        measurement_end = False
        last_buffer = []

        def sample_callback(
            task_handle, every_n_samples_event_type, number_of_samples, callback_data
        ):
            """Callback function for reading singals."""
            print("Every N Samples callback invoked.")

            global samples
            global trigger_control
            global measurement_end
            global last_buffer

            new_data = np.array(task.read(number_of_samples_per_channel=1000))

            new_data_z = np.sum(new_data[-4:], axis=0)

            global_samples.extend(new_data_z)

            threshold = (weight + load) * 0.0018 / (fz_range / 2.5) * 9.80665

            new_data_z_concat = np.concatenate((last_buffer, new_data_z))

            # Define the threshold
            above_threshold = new_data_z_concat > (threshold * 1.1)
            under_threshold = new_data_z_concat < threshold

            first_index = len(last_buffer)

            last_index = -1

            for i in range(len(last_buffer), len(new_data_z_concat) - 20):
                # test if the index is really situated at a threshold
                next_above_threshold = np.all(above_threshold[i : i + 20])
                next_under_threshold = np.all(under_threshold[i : i + 20])
                # if the trigger is off and the threshold is detected
                if not trigger_control and next_above_threshold and not measurement_end:
                    # find the first occurence in the 100 values before the index i where all the next values are above the threshold
                    first_index = i - np.argmax(under_threshold[i - 100 : i][::-1])
                    print("trigger on")
                    trigger_control = True
                # if the trigger is on and the data goes under the threshold
                if trigger_control and next_under_threshold and not measurement_end:
                    last_index = i
                    # filter that does not validate the measurement if the length is too short
                    if (len(samples) + last_index - first_index) > 100:
                        print("trigger off")
                        print(first_index)
                        print(last_index)
                        samples.extend(new_data_z_concat[first_index:last_index])
                        measurement_end = True
                    else:
                        samples = []
                        print("trigger off but measurement too short")
                    trigger_control = False

            # case if the trigger stays on at the end of the buffer reading
            if trigger_control:
                print("trigger control still on at the end of the buffer")
                samples.extend(new_data_z_concat[first_index:last_index])

            last_buffer = new_data_z

            return 0

        task.register_every_n_samples_acquired_into_buffer_event(1000, sample_callback)

        task.start()

        # timeout a bit more than 10s, otherwise there is conflict with the callback if the timeout
        # falls exactly on a second (for example 10s)
        timeout = time.time() + 5.5

        while True:
            # check if either the timeout is reached or the samples have been recorded but the trigger is now off
            if time.time() > timeout or measurement_end:
                print("break")
                break

    return samples, global_samples


def analyse_jump(data, weight, load, fz_range):
    num_samples = len(data)

    time = np.linspace(0, num_samples / sampling_rate, num_samples)

    # compute the force and velocity values
    sum_newton = np.array(data) / (0.0018 / (fz_range / 2.5))

    # force is very straight-forward
    mean_newton = np.mean(sum_newton)

    # we integrate the force to find the velocity
    if load is None:
        load = 0

    # acceleration is proportional to the force at every moment
    acceleration = (sum_newton / (weight + load)) - 9.80665

    # we find the velocity by doing the integral under the curve of the acceleration
    velocity = it.cumulative_trapezoid(acceleration, time, initial=0)

    mean_velocity = np.mean(velocity)

    power = sum_newton * velocity

    mean_power = np.mean(power)

    return (time, sum_newton, mean_newton, velocity, mean_velocity, mean_power)
