from dash import Input, Output, State, callback, ctx, no_update, html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from components import (
    ValueCard,
)
import numpy as np
from utils.utils import generate_table_data

height = 80
card_height = height / 3.5

SummaryTabContent = dbc.Col(
    [
        dbc.Row(
            children=[
                dbc.Col(html.H4("Résumé de la séance", className="m-2")),
                dbc.Col(dcc.Dropdown(multi=True, id="session-summary-dropdown")),
            ],
        ),
        # Mean Values Row
        dbc.Row(
            children=[
                dbc.Col(
                    ValueCard(
                        0,
                        "N",
                        "Force moyenne",
                        "session-summary-mean-force-card",
                        height=card_height,
                        h3_size="2vw",
                        h2_size="1vw",
                    ),
                    width=2,
                ),
                dbc.Col(
                    ValueCard(
                        0,
                        "N",
                        "Force max",
                        "session-summary-max-force-card",
                        height=card_height,
                        h3_size="2vw",
                        h2_size="1vw",
                    ),
                    width=2,
                ),
                dbc.Col(
                    ValueCard(
                        0,
                        "m/s",
                        "Vitesse moyenne",
                        "session-summary-mean-velocity-card",
                        height=card_height,
                        h3_size="2vw",
                        h2_size="1vw",
                    ),
                    width=2,
                ),
                dbc.Col(
                    ValueCard(
                        0,
                        "m/s",
                        "Vitesse max",
                        "session-summary-max-velocity-card",
                        height=card_height,
                        h3_size="2vw",
                        h2_size="1vw",
                    ),
                    width=2,
                ),
                dbc.Col(
                    ValueCard(
                        0,
                        "watt",
                        "Puissance moyenne",
                        "session-summary-mean-power-card",
                        height=card_height,
                        h3_size="2vw",
                        h2_size="1vw",
                    ),
                    width=2,
                ),
                dbc.Col(
                    ValueCard(
                        0,
                        "watt",
                        "Puissance max",
                        "session-summary-max-power-card",
                        height=card_height,
                        h3_size="2vw",
                        h2_size="1vw",
                    ),
                    width=2,
                ),
            ],
            class_name="mb-2",
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                html.H5("Force"),
                                dcc.Graph(
                                    id="session-summary-chart-force",
                                    style={"height": str(height * 0.60) + "vh"},
                                    figure=go.Figure().update_layout(
                                        margin=dict(l=10, r=10, t=10, b=20),
                                    ),
                                ),
                            ],
                        ),
                        style={"height": str(height / 1.35) + "vh"},
                    ),
                    width=6,
                    class_name="mb-2",
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                html.H5("Vitesse"),
                                dcc.Graph(
                                    id="session-summary-chart-velocity",
                                    style={"height": str(height * 0.60) + "vh"},
                                    figure=go.Figure().update_layout(
                                        margin=dict(l=10, r=10, t=10, b=20),
                                    ),
                                ),
                            ],
                        ),
                        style={"height": str(height / 1.35) + "vh"},
                    ),
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                html.Span("Force"),
                                dcc.Graph(
                                    id="session-summary-mean-chart-force",
                                    style={"height": str(height * 0.35) + "vh"},
                                    figure=go.Figure().update_layout(
                                        margin=dict(l=10, r=10, t=10, b=20),
                                    ),
                                ),
                            ],
                        ),
                        style={"height": str(height / 2.2) + "vh"},
                    ),
                    width=6,
                    class_name="mb-2",
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                html.Span("Vitesse"),
                                dcc.Graph(
                                    id="session-summary-mean-chart-velocity",
                                    style={"height": str(height * 0.35) + "vh"},
                                    figure=go.Figure().update_layout(
                                        margin=dict(l=10, r=10, t=10, b=20),
                                    ),
                                ),
                            ],
                        ),
                        style={"height": str(height / 2.2) + "vh"},
                    ),
                    width=6,
                    class_name="mb-2",
                ),
            ],
        ),
        dbc.Row(
            html.Div(
                id="session-summary-display-table",
                children=[
                    html.H4(
                        "Données de la séance",
                        className="text-center",
                    ),
                    dash_table.DataTable(
                        id="datatable-session-summary",
                        export_format="xlsx",
                        style_table={
                            "height": str(height * 10) + "px",
                            "overflowY": "auto",
                        },
                    ),
                ],
                className="mt-3",
            ),
        ),
        dcc.Store(id="session-summary-jump-id"),
    ],
    class_name="mt-2",
    width=12,
)


@callback(
    Output("session-summary-dropdown", "options"),
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
    Output("session-summary-jump-id", "data"),
    Input("session-summary-dropdown", "value"),
)
def store_jump_id(value):
    if value is not None:
        return value


@callback(
    Output("session-summary-chart-force", "figure"),
    Output("session-summary-chart-velocity", "figure"),
    Input("session-stop", "n_clicks"),
    State("session-jumps", "data"),
    State("session-summary-jump-id", "data"),
)
def display_all_jumps(s, jumps_data, jumps_id):
    if not jumps_data:
        raise PreventUpdate

    legend = dict(
        orientation="h", entrywidth=100, yanchor="top", y=-0.2, xanchor="right", x=1
    )

    fig_force = go.Figure()
    fig_velocity = go.Figure()

    if jumps_id not in [None, []]:
        jumps_data = [jumps_data[i] for i in jumps_id]

    for i, jump in enumerate(jumps_data):
        time, force, velocity, _ = jump
        fig_force.add_trace(
            go.Scatter(x=time, y=force, mode="lines", name=f"Mouvement {i+1}")
        )
        fig_velocity.add_trace(
            go.Scatter(x=time, y=velocity, mode="lines", name=f"Mouvement {i+1}")
        )

    fig_force.update_layout(
        margin=dict(l=10, r=10, t=10, b=20),
        xaxis_title="Time (s)",
        yaxis_title="Force (N)",
        legend=legend,
    )

    fig_velocity.update_layout(
        margin=dict(l=10, r=10, t=10, b=20),
        xaxis_title="Time (s)",
        yaxis_title="Velocity (m/s)",
        legend=legend,
    )

    return fig_force, fig_velocity


@callback(
    Output("session-summary-mean-force-card", "children"),
    Output("session-summary-max-force-card", "children"),
    Output("session-summary-mean-velocity-card", "children"),
    Output("session-summary-max-velocity-card", "children"),
    Output("session-summary-mean-power-card", "children"),
    Output("session-summary-max-power-card", "children"),
    Input("session-stop", "n_clicks"),
    State("session-metrics", "data"),
    State("session-summary-jump-id", "data"),
)
def display_summary_cards(stop, data, jumps_id):
    if not data:
        raise PreventUpdate

    if jumps_id not in [None, []]:
        jumps_data = []
        for j in range(len(data)):
            jumps_data.append([data[j][i] for i in jumps_id])
        data = jumps_data

    mean_forces = data[0]
    max_forces = data[1]
    mean_velocities = data[2]
    max_velocities = data[3]
    mean_powers = data[4]
    max_powers = data[5]

    return (
        round(np.mean(mean_forces), 0),
        round(np.mean(max_forces), 0),
        round(np.mean(mean_velocities), 2),
        round(np.mean(max_velocities), 2),
        round(np.mean(mean_powers), 0),
        round(np.mean(max_powers), 0),
    )


@callback(
    Output("datatable-session-summary", "data"),
    Input("session-metrics", "data"),
)
def display_session(data):
    if data is not None:
        table_data = generate_table_data(data)
        return table_data


@callback(
    Output("session-summary-mean-chart-force", "figure"),
    Output("session-summary-mean-chart-velocity", "figure"),
    Input("session-stop", "n_clicks"),
    State("session-metrics", "data"),
    State("session-summary-jump-id", "data"),
)
def display_summary_mean_max_charts(stop, data, jumps_id):
    if not data:
        raise PreventUpdate

    if jumps_id not in [None, []]:
        jumps_data = []
        for j in range(len(data)):
            jumps_data.append([data[j][i] for i in jumps_id])
        data = jumps_data

    mean_forces = data[0]
    max_forces = data[1]
    mean_velocities = data[2]
    max_velocities = data[3]

    legend = dict(
        orientation="h", entrywidth=120, yanchor="bottom", y=1.02, xanchor="right", x=1
    )
    margin = dict(l=0, r=0, t=0, b=0)
    font = dict(
        size=12,
    )

    force_fig = go.Figure()
    force_fig.add_trace(
        go.Scatter(
            x=list(range(1, len(mean_forces) + 1)),
            y=mean_forces,
            name="Force moyenne",
        )
    )
    force_fig.add_trace(
        go.Scatter(
            x=list(range(1, len(max_forces) + 1)),
            y=max_forces,
            name="Force max",
        )
    )
    force_fig.update_layout(
        xaxis_title="Répétition",
        yaxis_title="Force (N)",
        margin=margin,
        legend=legend,
        font=font,
    )

    velocity_fig = go.Figure()
    velocity_fig.add_trace(
        go.Scatter(
            x=list(range(1, len(mean_velocities) + 1)),
            y=mean_velocities,
            name="Vitesse moyenne",
        )
    )
    velocity_fig.add_trace(
        go.Scatter(
            x=list(range(1, len(max_velocities) + 1)),
            y=max_velocities,
            name="Vitesse max",
        )
    )
    velocity_fig.update_layout(
        xaxis_title="Répétition",
        yaxis_title="Vitesse (m/s)",
        margin=margin,
        legend=legend,
        font=font,
    )

    return force_fig, velocity_fig
