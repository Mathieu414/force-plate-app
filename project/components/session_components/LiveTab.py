from dash import Input, Output, State, callback, ctx, no_update, html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from components import (
    ValueCard,
)

height = 80
card_height = height / 3.5

LiveTabContent = dbc.Row(
    children=[
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Span("Objectif de vitesse"),
                                dbc.Input(
                                    id="velocity-goal",
                                    placeholder="Valeur...",
                                    type="number",
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                html.Span("Objectif de force"),
                                dbc.Input(
                                    id="force-goal",
                                    placeholder="Valeur...",
                                    type="number",
                                ),
                            ],
                        ),
                    ],
                    class_name="mb-2",
                ),
                dbc.Row(
                    children=[
                        dbc.Col(
                            ValueCard(
                                0,
                                "N",
                                "Force Max",
                                "session-live-maxforce-card",
                                height=card_height,
                                h3_size="2vw",
                                h2_size="1vw",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            ValueCard(
                                0,
                                "N",
                                "Force Moyenne",
                                "session-live-meanforce-card",
                                height=card_height,
                                h3_size="2vw",
                                h2_size="1vw",
                            ),
                            width=6,
                        ),
                    ],
                    class_name="mb-2",
                ),
                dbc.Row(
                    children=[
                        dbc.Col(
                            ValueCard(
                                0,
                                "m/s",
                                "Vitesse Max",
                                "session-live-maxvelocity-card",
                                height=card_height,
                                h3_size="2vw",
                                h2_size="1vw",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            ValueCard(
                                0,
                                "m/s",
                                "Vitesse Moyenne",
                                "session-live-meanvelocity-card",
                                height=card_height,
                                h3_size="2vw",
                                h2_size="1vw",
                            ),
                            width=6,
                        ),
                    ],
                    class_name="mb-2",
                ),
                dbc.Row(
                    children=[
                        dbc.Col(
                            ValueCard(
                                0,
                                "watt",
                                "Puissance Max",
                                "session-live-maxpower-card",
                                height=card_height,
                                h3_size="2vw",
                                h2_size="1vw",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            ValueCard(
                                0,
                                "watt",
                                "Puissance Moyenne",
                                "session-live-meanpower-card",
                                height=card_height,
                                h3_size="2vw",
                                h2_size="1vw",
                            ),
                            width=6,
                        ),
                    ]
                ),
            ],
            width=4,
        ),
        dbc.Col(
            children=[
                dbc.Row(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                html.Span("Force"),
                                dcc.Graph(
                                    id="session-live-mean-chart-force",
                                    style={"height": str(height * 0.35) + "vh"},
                                    figure=go.Figure().update_layout(
                                        margin=dict(l=10, r=10, t=10, b=20),
                                    ),
                                ),
                            ],
                        ),
                        style={"height": str(height / 2.2) + "vh"},
                    ),
                    class_name="mb-2",
                ),
                dbc.Row(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                html.Span("Vitesse"),
                                dcc.Graph(
                                    id="session-live-mean-chart-velocity",
                                    style={"height": str(height * 0.35) + "vh"},
                                    figure=go.Figure().update_layout(
                                        margin=dict(l=10, r=10, t=10, b=20),
                                    ),
                                ),
                            ],
                        ),
                        style={"height": str(height / 2.2) + "vh"},
                    ),
                    class_name="mb-2",
                ),
            ],
            width=8,
        ),
    ],
    justify="around",  # This will space the columns evenly
    class_name="m-2",
)


@callback(
    Output("session-live-meanforce-card", "children"),
    Output("session-live-maxforce-card", "children"),
    Output("session-live-meanvelocity-card", "children"),
    Output("session-live-maxvelocity-card", "children"),
    Output("session-live-meanpower-card", "children"),
    Output("session-live-maxpower-card", "children"),
    Input("session-metrics", "data"),
    Input("force-goal", "value"),
    Input("velocity-goal", "value"),
)
def display_metrics_cards(data, force_goal, velocity_goal):
    if not data:
        return (0, 0, 0, 0, 0, 0)

    mean_force = data[0][-1]
    max_force = data[1][-1]
    mean_velocity = data[2][-1]
    max_velocity = data[3][-1]
    mean_power = data[4][-1]
    max_power = data[5][-1] if len(data) > 5 else 0

    # Set colors based on goals
    if force_goal:
        if mean_force >= force_goal:
            mean_force_color = "green"
        else:
            mean_force_color = "red"
    else:
        mean_force_color = "inherit"
    if velocity_goal:
        if mean_velocity >= velocity_goal:
            mean_velocity_color = "green"
        else:
            mean_velocity_color = "red"
    else:
        mean_velocity_color = "inherit"

    return (
        html.Span(round(mean_force, 0), style={"color": mean_force_color}),
        round(max_force, 0),
        html.Span(round(mean_velocity, 2), style={"color": mean_velocity_color}),
        round(max_velocity, 2),
        round(mean_power, 0),
        round(max_power, 0),
    )


@callback(
    Output("session-live-mean-chart-force", "figure"),
    Output("session-live-mean-chart-velocity", "figure"),
    Input("session-metrics", "data"),
    Input("force-goal", "value"),
    Input("velocity-goal", "value"),
)
def display_mean_max_charts(data, force_goal, velocity_goal):
    mean_forces = data[0] if data is not None else []
    max_forces = data[1] if data is not None else []
    mean_velocities = data[2] if data is not None else []
    max_velocities = data[3] if data is not None else []

    legend = dict(
        orientation="h", entrywidth=120, yanchor="bottom", y=1.02, xanchor="right", x=1
    )
    margin = dict(l=0, r=0, t=0, b=0)
    font = dict(
        size=12,
    )

    # Create colors arrays based on goals
    mean_force_colors = [
        "green" if force_goal and val >= force_goal else "blue" for val in mean_forces
    ]
    mean_velocity_colors = [
        "green" if velocity_goal and val >= velocity_goal else "blue"
        for val in mean_velocities
    ]

    force_fig = go.Figure(
        data=[
            go.Bar(
                x=list(range(1, len(mean_forces) + 1)),
                y=mean_forces,
                name="Force moyenne",
                marker_color=mean_force_colors,
            ),
            go.Bar(
                x=list(range(1, len(max_forces) + 1)),
                y=max_forces,
                name="Force max",
            ),
        ]
    )

    # Add horizontal line for force goal if set
    if force_goal:
        force_fig.add_shape(
            type="line",
            x0=0,
            y0=force_goal,
            x1=len(mean_forces) + 1,
            y1=force_goal,
            line=dict(color="red", width=2, dash="dash"),
        )

    force_fig.update_layout(
        xaxis_title="Répétition",
        yaxis_title="Force (N)",
        barmode="group",
        margin=margin,
        legend=legend,
        font=font,
    )

    velocity_fig = go.Figure(
        data=[
            go.Bar(
                x=list(range(1, len(mean_velocities) + 1)),
                y=mean_velocities,
                name="Vitesse moyenne",
                marker_color=mean_velocity_colors,
            ),
            go.Bar(
                x=list(range(1, len(max_velocities) + 1)),
                y=max_velocities,
                name="Vitesse max",
            ),
        ]
    )

    # Add horizontal line for velocity goal if set
    if velocity_goal:
        velocity_fig.add_shape(
            type="line",
            x0=0,
            y0=velocity_goal,
            x1=len(mean_velocities) + 1,
            y1=velocity_goal,
            line=dict(color="red", width=2, dash="dash"),
        )

    velocity_fig.update_layout(
        xaxis_title="Répétition",
        yaxis_title="Vitesse (m/s)",
        barmode="group",
        margin=margin,
        legend=legend,
        font=font,
    )
    return force_fig, velocity_fig
