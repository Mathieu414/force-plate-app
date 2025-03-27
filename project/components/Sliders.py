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
    ],
)

Sliders = html.Div(
    [
        dbc.Button(
            html.I(className="fa fa-gear fa-xl"),
            color="light",
            id="collapse-button",
        ),
        dbc.Collapse(sliders_content, id="collapse", is_open=False),
    ]
)

SlidersModal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Paramétrage de Fzi")),
        dbc.ModalBody(children=[sliders_content]),
        dbc.ModalFooter(dbc.Button("Fermer", id="close-range-modal", n_clicks=0)),
    ],
    id="range-modal",
    is_open=False,
)


@callback(
    Output("range-modal", "is_open"),
    [Input("open-range-modal", "n_clicks"), Input("close-range-modal", "n_clicks")],
    [State("range-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
