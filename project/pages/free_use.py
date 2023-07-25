import dash
from dash import html, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc

import pandas as pd

df = pd.DataFrame()

collection = None

dash.register_page(__name__, path="/libre")

layout = html.Div()
