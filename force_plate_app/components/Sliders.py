import dash_bootstrap_components as dbc
from dash import html, dcc

Sliders = dbc.Row(
    [
        dbc.Col(
            children=[
                html.H3("Range de Fzi"),
                dcc.Slider(
                    0.25,
                    5,
                    step=None,
                    marks={
                        0.25: "250N",
                        0.5: "500N",
                        2.5: "2.5kN",
                        5: "5kN",
                    },
                    value=2.5,
                    id="range-slider",
                ),
            ],
            class_name="text-center",
        ),
        dbc.Col(
            children=[
                html.H3("Range de Fxi, Fyi"),
                dcc.Slider(
                    0.125,
                    2.5,
                    step=None,
                    marks={
                        0.125: "125N",
                        0.25: "250N",
                        1.25: "1.25kN",
                        2.5: "2.5kN",
                    },
                    value=2.5,
                    id="range-slider-xy",
                ),
            ],
            class_name="text-center",
        ),
    ],
)
