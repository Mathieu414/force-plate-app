import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, callback, dcc, ctx
from dash.exceptions import PreventUpdate
import nidaqmx
import time
from utils.nidaq import nidaq_base_config


def WeightCard(height=38):
    return (
        dbc.Card(
            class_name="text-center",
            children=dbc.CardBody(
                children=[
                    html.H3(
                        className="mb-1 mt-2 card-title",
                        style={"font-size": "3vw"},
                        children="0",
                        id="display-user-weight-1",
                    ),
                    html.H2("KG"),
                    html.Small(
                        children="Poids de l'athlète sans charge",
                    ),
                    html.Div(
                        className="text-center",
                        children=[
                            dbc.Button(
                                "Mesurer",
                                color="info",
                                id="user-weighting-1",
                            ),
                        ],
                    ),
                    html.P(["Poids actuel : ", html.Span(id="weight-display")]),
                ],
                class_name="my-auto",
                style={"flex": 0},
            ),
            style={"height": str(height) + "vh"},
        ),
        dcc.Store(id="weight-data", storage_type="session"),
    )


@callback(
    Output("display-user-weight-1", "children"),
    Output("weight-data", "data"),
    Input("user-weighting-1", "n_clicks"),
    State("fz-range", "data"),
    prevent_initial_call=True,
)
def display_weight(n_clicks, value):
    print("--display_weight--")
    with nidaqmx.Task() as task:
        data = nidaq_base_config(task)

    mean_z = []

    for i in range(4, 8):
        print(i)
        print(sum(data[i]) / len(data[i]))
        mean_z.append((sum(data[i]) / len(data[i])) * 56.6509007 * (value / 2.5))

    return round(sum(mean_z), 2), sum(mean_z)


@callback(
    Output("weight-display", "children"),
    Input("weight-data", "data"),
    State("fz-range", "data"),
)
def display_weight(data, value):
    if data is not None:
        data = data * 9.80665
        return round(data, 2)
    else:
        return "Pas de donnée"
