from dash import Input, Output, State, callback, ctx, no_update, html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from components import (
    WeightCard,
)

height = 60

MainTabContent = dbc.Row(
    [
        dbc.Col(
            children=[
                dbc.Card(
                    dbc.CardBody(
                        children=[
                            html.H5("Mouvement"),
                            dcc.Graph(
                                id="session-chart",
                                style={"height": str(height * 0.8) + "vh"},
                                figure=go.Figure().update_layout(
                                    margin=dict(l=10, r=10, t=10, b=20),
                                ),
                            ),
                        ],
                    ),
                    style={"height": str(height) + "vh"},
                ),
            ],
            width=9,
        ),
        dbc.Col(
            children=[
                dbc.Row(WeightCard(height=(height - 10))),
                dbc.Row(
                    dbc.Input(
                        placeholder="Charge supplémentaire (kg)",
                        type="number",
                        min=0,
                        id="load-input-session",
                    ),
                    class_name="mt-2",
                ),
            ],
            width=3,
        ),
    ],
    class_name="mt-2",
)
