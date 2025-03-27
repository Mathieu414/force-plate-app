import dash
from dash import html
import dash_bootstrap_components as dbc
from components import TestIntroCard, ConnectionAlert
from utils.nidaq import check_force_plate_connection

dash.register_page(__name__, path="/")

layout = html.Div(
    id="home",
    children=[
        dbc.Row(
            [
                TestIntroCard,
            ]
        ),
        dbc.Row(id="connection-alert-div"),
    ],
)


@dash.callback(
    dash.Output("connection-alert-div", "children"), dash.Input("home", "children")
)
def update_connection_alert(_):
    return ConnectionAlert(check_force_plate_connection())
