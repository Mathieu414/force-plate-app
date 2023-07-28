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
)
from components import Sliders, StartStopCalibrate, WeightCard, ValueCard
from components.GraphCard import nidaq_trigger, analyse_jump
import plotly.express as px

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
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        children=[
                            html.H4("Mouvement total"),
                            dcc.Graph(
                                id="session-global-chart",
                                style={"height": "32vh"},
                                figure=go.Figure().update_layout(
                                    margin=dict(l=10, r=10, t=10, b=20),
                                ),
                            ),
                        ],
                    ),
                    style={"height": "40vh"},
                ),
            ),
            class_name="mb-2",
            # style={"display": "none"},
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
                            className="mt-3 mb-2",
                        ),
                        dbc.Input(
                            placeholder="Charge supplémentaire (kg)",
                            size="lg",
                            type="number",
                            min=0,
                            id="load-input-session",
                        ),
                    ],
                    align="center",
                    class_name="text-center",
                    width=4,
                ),
                dbc.Col(ValueCard(0, "N", "Force", "session-force-card", height=30)),
                dbc.Col(
                    ValueCard(0, "m/s", "Vitesse", "session-speed-card", height=30)
                ),
                dbc.Col(
                    ValueCard(0, "watt", "Puissance", "session-power-card", height=30)
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
                                dbc.Row(
                                    children=[
                                        dbc.Col(
                                            children=[
                                                dbc.Button(
                                                    html.I(className="fas fa-list"),
                                                    id="choice-list",
                                                ),
                                                dbc.Button(
                                                    html.I(
                                                        className="fas fa-chart-line"
                                                    ),
                                                    id="choice-chart",
                                                ),
                                            ]
                                        ),
                                        dbc.Col(
                                            children=[
                                                dbc.Button("N", id="type-force"),
                                                dbc.Button("M/S", id="type-speed"),
                                                dbc.Button("Watt", id="type-power"),
                                            ],
                                            class_name="text-end",
                                            id="units-buttons",
                                        ),
                                    ],
                                    justify="between",
                                ),
                                html.Div(
                                    id="session-display",
                                    style={"height": "60vh"},
                                    children=[
                                        html.Div(
                                            id="session-display-graph",
                                            children=[
                                                html.H4(
                                                    "Graphique de la séance",
                                                    className="text-center",
                                                ),
                                                dcc.Graph(id="session-summary-chart"),
                                            ],
                                        ),
                                        html.Div(
                                            id="session-display-table",
                                            children=[
                                                html.H4(
                                                    "Données de la séance",
                                                    className="text-center",
                                                ),
                                                dash_table.DataTable(
                                                    id="datatable-session",
                                                    editable=True,
                                                    row_deletable=True,
                                                    export_format="xlsx",
                                                    style_table={
                                                        "height": "370px",
                                                        "overflowY": "auto",
                                                    },
                                                ),
                                            ],
                                            className="mt-3",
                                            style={"display": "none"},
                                        ),
                                    ],
                                ),
                                dbc.Button(
                                    id="reset-session-data",
                                    children="Remettre à zéro",
                                    color="danger",
                                ),
                            ]
                        )
                    ),
                    width=112,
                ),
            ]
        ),
        dcc.Interval(
            id="interval-component", interval=1 * 500, n_intervals=0, disabled=True
        ),
        dbc.Button(id="interval-controller", style={"display": "none"}),
        dcc.Store(id="session-data", storage_type="session"),
        # component to store if the session-display is displaying a graph or a table
        dcc.Store(id="session-display-type", storage_type="session", data="graph"),
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
    Output("interval-controller", "n_clicks"),
    Input("interval-component", "n_intervals"),
    prevent_initial_call=True,
)
def loop_handling(n):
    if not is_recording:
        return 1
    else:
        raise PreventUpdate


@callback(
    Output("session-data", "data"),
    Output("session-chart", "figure"),
    Output("session-global-chart", "figure"),
    Output("session-force-card", "children"),
    Output("session-speed-card", "children"),
    Output("session-power-card", "children"),
    Input("interval-controller", "n_clicks"),
    Input("reset-session-data", "n_clicks"),
    Input("session-start", "n_clicks"),
    Input("datatable-session", "derived_virtual_data"),
    State("weight-data", "data"),
    State("load-input-session", "value"),
    State("session-data", "data"),
    State("fz-range", "data"),
    prevent_initial_call=True,
)
def session_trigger(n, start, reset, rows, weight, load, stored_data, fz_range):
    if ctx.triggered_id == "reset-session-data":
        print("reset session data")
        return (None, no_update, no_update, no_update, no_update, no_update)
    if ctx.triggered_id == "datatable-session":
        print("data_table_interactivity")
        if stored_data is not None:
            new_stored_data = stored_data
            if rows != []:
                df = pd.DataFrame(rows)
                new_stored_data = [
                    df["Force (N)"].values.tolist(),
                    df["Vitesse (m/s)"].values.tolist(),
                    df["Puissance (Watts)"].values.tolist(),
                ]
            if new_stored_data != stored_data:
                return (
                    new_stored_data,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )
            else:
                raise PreventUpdate
        else:
            raise PreventUpdate
    else:
        global is_recording
        is_recording = True
        data, global_data = nidaq_trigger(weight, load, fz_range=fz_range)

        if data == []:
            is_recording = False
            raise PreventUpdate
        else:
            (
                time,
                sum_newton,
                mean_newton,
                velocity,
                mean_velocity,
                mean_power,
            ) = analyse_jump(data, weight, load, fz_range=fz_range)

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=time, y=sum_newton, mode="lines", name=("Vertical force (N)")
                )
            )
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=20),
                xaxis_title="Temps (s)",
                yaxis_title="Force (N)",
            )

            global_time = np.linspace(
                0, len(global_data) / sampling_rate, len(global_data)
            )

            global_fig = go.Figure().add_trace(
                go.Scatter(
                    x=global_time,
                    y=np.array(global_data) / (0.0018 / (fz_range / 2.5)),
                    mode="lines",
                    name=("Vertical force (N)"),
                )
            )
            global_fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=20),
                xaxis_title="Temps (s)",
                yaxis_title="Force (N)",
            )
            is_recording = False

            if stored_data is None:
                print("storing data for the first time")
                stored_data = np.array([[mean_newton], [mean_velocity], [mean_power]])
            else:
                stored_data = np.append(
                    stored_data, [[mean_newton], [mean_velocity], [mean_power]], axis=1
                )

            return (
                stored_data,
                fig,
                global_fig,
                round(mean_newton, 2),
                round(mean_velocity, 2),
                round(mean_power, 2),
            )


@callback(
    Output("session-summary-chart", "figure"),
    Output("session-display-graph", "style"),
    Output("datatable-session", "data"),
    Output("session-display-table", "style"),
    Output("session-display-type", "data"),
    Input("choice-list", "n_clicks"),
    Input("choice-chart", "n_clicks"),
    Input("type-force", "n_clicks"),
    Input("type-speed", "n_clicks"),
    Input("type-power", "n_clicks"),
    Input("session-data", "data"),
    State("session-display-type", "data"),
)
def display_session(l, c, f, s, p, data, display_type):
    if data is not None:
        if ctx.triggered_id == "choice-list":
            table_data = generate_table_data(data)
            return (no_update, {"display": "none"}, table_data, None, "table")
        if ctx.triggered_id == "choice-chart":
            fig = generate_graph(data[0], "Force (N)", "Force : %{y:.2f} N ")
            return (fig, None, no_update, {"display": "none"}, "graph")
        if ctx.triggered_id == "type-speed":
            fig = generate_graph(data[1], "Vitesse (M/S)", None)
            return (fig, None, no_update, {"display": "none"}, "graph")
        if ctx.triggered_id == "type-power":
            fig = generate_graph(data[2], "Puissance (Watts)", None)
            return (fig, None, no_update, {"display": "none"}, "graph")
        else:
            fig = generate_graph(data[0], "Force (N)", "Force : %{y:.2f} N ")
            table_data = generate_table_data(data)
            if display_type == "graph":
                return (fig, None, table_data, {"display": "none"}, "graph")
            else:
                return (fig, {"display": "none"}, table_data, None, "table")
    else:
        return (go.Figure(), no_update, no_update, no_update, no_update)


@callback(
    Output("units-buttons", "style"),
    Input("choice-list", "n_clicks"),
    Input("choice-chart", "n_clicks"),
)
def units_buttons(list, chart):
    if ctx.triggered_id == "choice-list":
        return {"display": "none"}
    else:
        return None


# function to generate the table from the display_session callback
def generate_table_data(data):
    df = pd.DataFrame(data).transpose()
    df.columns = ["Force (N)", "Vitesse (m/s)", "Puissance (Watts)"]
    df = df.round(2)
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
    )

    fig.update_traces(hovertemplate=hovertemplate)
    return fig
