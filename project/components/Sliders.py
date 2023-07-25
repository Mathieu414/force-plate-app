import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State

sliders_content = dbc.Row(
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

Sliders = html.Div(
    [
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    html.I(className="fa fa-gear fa-xl"),
                    color="light",
                    id="collapse-button",
                ),
                width=1,
            ),
            justify="end",
        ),
        dbc.Collapse(sliders_content, id="collapse", is_open=False),
    ]
)


@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
