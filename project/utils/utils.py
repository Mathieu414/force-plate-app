import numpy as np
import scipy.integrate as it
import pandas as pd
import plotly.express as px
import scipy


def substract_arrays(arr_1, arr_2):
    """substract arr_2 to arr_1. arr_2[0] is a number, and is substracted to arr_1[0], which is a list

    Args:
        arr_1 (list of list):
        arr_2 (list of numbers)

    Returns:
        list of list: substracted list
    """

    arr_2 = np.array(arr_2).reshape(len(arr_2), 1) if arr_2 else arr_2

    data = np.array(arr_1)

    data = data - arr_2 if arr_2 is not None else data

    return data


def analyse_jump(
    data: np.ndarray, weight: float, load: float, fz_range: float, sampling_rate: float
) -> dict:
    """utility function to compute metrics from a set of data. The data corresponds to a jump,
    and represents tension value in Volt.

    Args:
        data (np.ndarray): 1-d numpy array containing data from the jump, in V.
        weight (float): weight data, in kg
        load (float): load data, in kg
        fz_range (float): one of 5, 2.5, 0.5 or 0.25
        sampling_rate (float): sampling rate coming from nidaq config

    Returns:
        dict: Contains metrics for the jump:
            - time: Time points for the data
            - force: Force values in Newtons
            - mean_force: Mean force value
            - velocity: Velocity values
            - mean_velocity: Mean velocity value
            - power: Power values
            - mean_power: Mean power value
            - rate_of_force_development: RFD values
            - max_rfd: Maximum rate of force development
            - jump_height: Maximum jump height
            - gct: Ground contact time
            - rsi: Reactive strength index
    """
    num_samples = len(data)

    time = np.linspace(0, num_samples / sampling_rate, num_samples)

    volt_newton_convertion = 1 / (0.0018 / (fz_range / 2.5))

    # compute the force and velocity values
    force = np.array(data) * volt_newton_convertion

    # force is very straight-forward
    mean_force = np.mean(force)

    # we integrate the force to find the velocity
    if load is None:
        load = 0

    # acceleration is proportional to the force at every moment
    acceleration = (force - (weight + load) * 9.81) / (weight + load)

    # we find the velocity by doing the integral under the curve of the acceleration
    velocity = it.cumulative_trapezoid(acceleration, time, initial=0)

    mean_velocity = np.mean(velocity)

    power = force * velocity

    mean_power = np.mean(power)

    # Calculate Rate of Force Development (RFD)
    # Finding the maximum rate of change in force
    force_diff = np.diff(force)
    time_diff = np.diff(time)
    rate_of_force_development = force_diff / time_diff
    max_rfd = np.max(rate_of_force_development)

    # Calculate Ground Contact Time (GCT)
    # Identify when force exceeds body weight (contact with ground)
    contact_threshold = (weight + load) * 9.81 * 1.1  # 10% above body weight
    contact_indices = np.where(force > contact_threshold)[0]
    if len(contact_indices) > 0:
        gct = (contact_indices[-1] - contact_indices[0]) / sampling_rate
    else:
        gct = 0  # No contact detected

    # Calculate Reactive Strength Index (RSI)
    # RSI = jump height / ground contact time
    # First find the jump height from maximum velocity
    if np.max(velocity) > 0:
        jump_height = np.max(velocity) ** 2 / (2 * 9.81)
        rsi = jump_height / gct if gct > 0 else 0
    else:
        jump_height = 0
        rsi = 0

    return {
        "time": time,
        "force": force,
        "mean_force": mean_force,
        "velocity": velocity,
        "mean_velocity": mean_velocity,
        "power": power,
        "mean_power": mean_power,
        "rate_of_force_development": rate_of_force_development,
        "max_rfd": max_rfd,
        "jump_height": jump_height,
        "gct": gct,
        "rsi": rsi,
    }


# function to generate the table from the display_session callback
def generate_table_data(data):
    df = pd.DataFrame(data).transpose()
    df.columns = [
        "Force moyenne (N)",
        "Force max (N)",
        "Vitesse moyenne (m/s)",
        "Vitesse max (m/s)",
        "Puissance moyenne (Watts)",
        "Puissance max (Watts)",
        "RFD moyen (N/s)",
        "RFD max (N/s)",
        "Hauteur de saut (m)",
        "GCT (s)",
        "RSI",
    ]
    df = df.round(2)
    df = df.reset_index()
    df = df.rename(columns={"index": "Mouvement"})
    return df.to_dict("records")


# function to generate the graph from the display_session callback
def generate_graph(data, y_axis_title, hovertemplate):
    fig = px.bar(
        x=range(1, len(data) + 1),
        y=data,
    )
    fig.update_xaxes(type="category")
    fig.update_layout(
        yaxis_title=y_axis_title,
        xaxis_title="Répétition",
        hovermode="x",
        margin=dict(l=10, r=10, t=10, b=20),
    )

    fig.update_traces(hovertemplate=hovertemplate)
    return fig


VOLT_NEWTON = 0.0018
BASE_RANGE = 2.5


def convert_voltage_to_force(data, fz_range):
    """
    Convert voltage values to force values.

    This function takes voltage data from force plates and converts it to force units (Newtons)
    based on the specified force range.

    Parameters:
    ----------
    data : list or numpy.ndarray
        Voltage data to be converted.
    fz_range : float
        The force range in Newtons. This is used to scale the conversion factor.

    Returns:
    -------
    numpy.ndarray
        Converted force data in Newtons.

    Notes:
    -----
    The conversion uses the formula:
        force = voltage / (volt_newton / (fz_range / base_range))
    where:
        - volt_newton is 0.0018 V/N (voltage per Newton)
        - base_range is 2.5 N (reference force range)
    """
    data = np.array(data)
    data_converted = data / (VOLT_NEWTON / (fz_range / BASE_RANGE))
    return data_converted


def convert_force_to_voltage(data, fz_range):
    """
    Convert force values to voltage values.

    This function takes force data in Newtons and converts it to voltage units
    based on the specified force range.

    Parameters:
    ----------
    data : list or numpy.ndarray
        Force data in Newtons to be converted.
    fz_range : float
        The force range in Newtons. This is used to scale the conversion factor.

    Returns:
    -------
    numpy.ndarray
        Converted voltage data in Volts.

    Notes:
    -----
    The conversion uses the formula:
        voltage = force * (volt_newton / (fz_range / base_range))
    where:
        - volt_newton is 0.0018 V/N (voltage per Newton)
        - base_range is 2.5 N (reference force range)
    """
    data = np.array(data)
    data_converted = data * (VOLT_NEWTON / (fz_range / BASE_RANGE))
    return data_converted


def low_filter(data: np.ndarray, threshold: float):
    data_filtered = data.copy()
    for j in range(data.shape[0]):
        # deal with edge cases
        if threshold * 3 < data[j, 1] - data[j, 0]:
            data_filtered[j, 0] = data[j, 1]
        if threshold * 3 < data[j, -2] - data[j, -1]:
            data_filtered[j, -1] = data[j, -2]
        # remove artifacts
        for i in range(1, data.shape[1] - 1):
            if (threshold < data[j, i - 1] - data[j, i]) and (
                threshold < data[j, i + 1] - data[j, i]
            ):
                # Interpolate using adjacent values
                data_filtered[j, i] = (data[j, i - 1] + data[j, i + 1]) / 2
    return data_filtered
