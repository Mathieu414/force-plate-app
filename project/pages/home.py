import dash
from dash import html
import dash_bootstrap_components as dbc
from components import TestIntroCard

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        dbc.Row(
            [
                TestIntroCard,
            ]
        ),
    ]
)
