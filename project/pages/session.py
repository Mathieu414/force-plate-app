import dash
from dash import html, Output, Input, callback, ctx, dcc
import dash_bootstrap_components as dbc
from components import (
    ValueCard,
    GraphCard,
    StartStopCalibrate,
    CalibrationModal,
    WeightCard,
    Sliders,
)

dash.register_page(__name__, path="/seance")

layout = html.Div(
    [
        Sliders,
    ]
)
