from dash import Input, Output, State, callback, ctx, no_update, html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from components import (
    ValueCard,
)
import numpy as np
from utils.utils import convert_voltage_to_force

height = 70
card_height = height / 3.5

DetailsTabContent = dbc.Col(
    children=[
        dbc.Row(dcc.Dropdown(id="session-details-dropdown", value=0)),
        dbc.Row(
            children=[
                dbc.Col(
                    ValueCard(
                        card_id="rfd-max-card",
                        card_description="RFD max",
                        card_tail="N/s",
                        card_value=0,
                        h3_size="2vw",
                        h2_size="1vw",
                    ),
                    width=3,
                ),
                dbc.Col(
                    ValueCard(
                        card_id="jump-height-card",
                        card_description="Hauteur de saut",
                        card_tail="m",
                        card_value=0,
                        h3_size="2vw",
                        h2_size="1vw",
                    ),
                    width=3,
                ),
                dbc.Col(
                    ValueCard(
                        card_id="gct-card",
                        card_description="GCT",
                        card_tail="s",
                        card_value=0,
                        h3_size="2vw",
                        h2_size="1vw",
                    ),
                    width=3,
                ),
                dbc.Col(
                    ValueCard(
                        card_id="rsi-card",
                        card_description="RSI",
                        card_tail="",
                        card_value=0,
                        h3_size="2vw",
                        h2_size="1vw",
                    ),
                    width=3,
                ),
            ],
            class_name="m-2",
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                dcc.Graph(
                                    id="session-details-chart-cop",
                                    style={"height": str(height * 0.9) + "vh"},
                                    figure=go.Figure().update_layout(
                                        margin=dict(l=10, r=10, t=10, b=20),
                                    ),
                                ),
                            ],
                        ),
                        style={"height": str(height) + "vh"},
                    ),
                    class_name="m-2",
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                dcc.Graph(
                                    id="session-details-chart-cop-2d",
                                    style={"height": str(height * 0.9) + "vh"},
                                    figure=go.Figure().update_layout(
                                        margin=dict(l=10, r=10, t=10, b=20),
                                    ),
                                ),
                            ],
                        ),
                        style={"height": str(height) + "vh"},
                    ),
                    class_name="m-2",
                ),
            ],
        ),
        dcc.Store(id="session-detail-jump-id"),
    ],
    class_name="mt-2",
    width=12,
)


@callback(
    Output("session-details-dropdown", "options"),
    Input("session-stop", "n_clicks"),
    State("session-jumps", "data"),
)
def display_options(s, data):
    choices = []
    if data is not None:
        for i, _ in enumerate(data):
            choices.append({"label": f"Mouvement {i+1}", "value": i})
        return choices
    else:
        raise PreventUpdate


@callback(
    Output("session-detail-jump-id", "data"), Input("session-details-dropdown", "value")
)
def store_jump_id(value):
    if value is not None:
        return value


@callback(
    [
        Output("rfd-max-card", "children"),
        Output("jump-height-card", "children"),
        Output("gct-card", "children"),
        Output("rsi-card", "children"),
    ],
    Input("session-detail-jump-id", "data"),
    State("session-metrics", "data"),
)
def update_metric_cards(jump_id, metrics_data):
    if jump_id is None or metrics_data is None or len(metrics_data) <= jump_id:
        return 0, 0, 0, 0

    # Get metrics data for the selected jump
    # Columns 6, 7, 8, and 10 correspond to RFD max, Jump Height, GCT, and RSI
    metrics_data = np.array(metrics_data)
    jump_metrics = metrics_data[:, jump_id]

    rfd_max = (
        f"{jump_metrics[7]:.2f}" if isinstance(jump_metrics[7], (int, float)) else 0
    )
    jump_height = (
        f"{jump_metrics[8]:.3f}" if isinstance(jump_metrics[8], (int, float)) else 0
    )
    gct = f"{jump_metrics[9]:.3f}" if isinstance(jump_metrics[9], (int, float)) else 0
    rsi = f"{jump_metrics[10]:.2f}" if isinstance(jump_metrics[10], (int, float)) else 0

    return rfd_max, jump_height, gct, rsi


@callback(
    Output("session-details-chart-cop", "figure"),
    Input("session-stop", "n_clicks"),
    Input("session-detail-jump-id", "data"),
    State("session-jumps", "data"),
)
def display_cop(s, jump_id, data):
    if jump_id is None or data is None:
        raise PreventUpdate
    time, _, velocity, tension_data = data[jump_id]

    force_data_x = convert_voltage_to_force(tension_data[0], fz_range=2.5)
    force_data_y = convert_voltage_to_force(tension_data[1], fz_range=2.5)
    force_data_z = convert_voltage_to_force(tension_data[2], fz_range=2.5)

    # force plate coefficients
    b = 225
    a = 175

    # Calculate total force in z direction at each time point
    fz_total = np.zeros_like(force_data_z[0])
    for i in range(4):  # Assuming 4 sensors
        fz_total += np.array(force_data_z[i])

    # Convert time to numpy array
    time_array = np.array(time)

    az = np.zeros_like(time_array)  # Position in z-direction

    # Integrate acceleration to get velocity, and velocity to get position
    for i in range(1, len(time_array)):
        delta_t = time_array[i] - time_array[i - 1]

        # Integration for position
        az[i] = az[i - 1] + velocity[i - 1] * delta_t * 1000

    # Calculate center of pressure coordinates at each time point
    ax = np.zeros_like(time_array)
    ay = np.zeros_like(time_array)

    # Calculate moments at each time point
    mx_array = np.zeros_like(time_array)
    my_array = np.zeros_like(time_array)

    for i in range(len(time_array)):
        # Calculate moments for each time point
        mx_array[i] = b * (
            force_data_z[0][i]
            + force_data_z[1][i]
            - force_data_z[2][i]
            - force_data_z[3][i]
        )
        my_array[i] = a * (
            -force_data_z[0][i]
            + force_data_z[1][i]
            + force_data_z[2][i]
            - force_data_z[3][i]
        )

        # Avoid division by zero
        if abs(fz_total[i]) > 1e-6:  # Threshold to avoid division by very small numbers
            ax[i] = -my_array[i] / fz_total[i]
            ay[i] = mx_array[i] / fz_total[i]
        else:
            # If force is too small, keep previous position or set to zero
            if i > 0:
                ax[i] = ax[i - 1]
                ay[i] = ay[i - 1]
            else:
                ax[i] = 0
                ay[i] = 0

    # Create a 3D plot for COP trajectory
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=ax,
                y=ay,
                z=az,
                mode="lines+markers",
                marker=dict(
                    size=2,
                    color=time_array,  # Color points by time
                    colorscale="Viridis",
                    opacity=0.8,
                ),
                line=dict(color="darkblue", width=2),
                name="COP Trajectory",
            )
        ]
    )

    z_max = np.max(az)

    # Update layout for better visualization
    fig.update_layout(
        title="Center of Pressure 3D Trajectory",
        scene=dict(
            xaxis=dict(range=[-a, a]),
            yaxis=dict(range=[-b, b]),
            xaxis_title="COP X (mm)",
            yaxis_title="COP Y (mm)",
            zaxis_title="Height (mm)",
            aspectmode="manual",
            aspectratio=dict(x=(a * 2 / z_max), y=(b * 2 / z_max), z=1),
        ),
        margin=dict(l=10, r=10, t=40, b=10),
    )

    return fig


@callback(
    Output("session-details-chart-cop-2d", "figure"),
    Input("session-stop", "n_clicks"),
    Input("session-detail-jump-id", "data"),
    State("session-jumps", "data"),
)
def display_cop_2d_histogram(s, jump_id, data):
    if jump_id is None or data is None:
        raise PreventUpdate

    time, _, velocity, tension_data = data[jump_id]

    force_data_x = convert_voltage_to_force(tension_data[0], fz_range=2.5)
    force_data_y = convert_voltage_to_force(tension_data[1], fz_range=2.5)
    force_data_z = convert_voltage_to_force(tension_data[2], fz_range=2.5)

    # force plate coefficients
    b = 225
    a = 175

    # Calculate total force in z direction at each time point
    fz_total = np.zeros_like(force_data_z[0])
    for i in range(4):  # Assuming 4 sensors
        fz_total += np.array(force_data_z[i])

    # Calculate center of pressure coordinates
    ax = np.zeros_like(fz_total)
    ay = np.zeros_like(fz_total)

    # Calculate moments
    mx_array = np.zeros_like(fz_total)
    my_array = np.zeros_like(fz_total)

    for i in range(len(fz_total)):
        mx_array[i] = b * (
            force_data_z[0][i]
            + force_data_z[1][i]
            - force_data_z[2][i]
            - force_data_z[3][i]
        )
        my_array[i] = a * (
            -force_data_z[0][i]
            + force_data_z[1][i]
            + force_data_z[2][i]
            - force_data_z[3][i]
        )

        if abs(fz_total[i]) > 1e-6:
            ax[i] = -my_array[i] / fz_total[i]
            ay[i] = mx_array[i] / fz_total[i]
        else:
            if i > 0:
                ax[i] = ax[i - 1]
                ay[i] = ay[i - 1]
            else:
                ax[i] = 0
                ay[i] = 0

    # Create a 2D histogram with adjusted density
    fig = go.Figure()
    # Add heatmap for better visualization of density
    fig.add_trace(
        go.Histogram2d(
            x=ax,
            y=ay,
            colorscale="Viridis",
            xbins=dict(
                start=-a, end=a, size=a / 20
            ),  # Set bins to cover full plate width
            ybins=dict(
                start=-b, end=b, size=b / 20
            ),  # Set bins to cover full plate height
            hoverinfo="skip",
        )
    )

    # Update layout
    fig.update_layout(
        title="Center of Pressure Distribution",
        xaxis=dict(
            title="COP X (mm)",
            range=[-a - 10, a + 10],
        ),
        yaxis=dict(
            title="COP Y (mm)",
            range=[-b - 10, b + 10],
            scaleanchor="x",
            scaleratio=1,
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        coloraxis_showscale=True,
        coloraxis_colorbar=dict(
            title="Density",
        ),
    )

    return fig
