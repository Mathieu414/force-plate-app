import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, callback, dcc, ctx
from dash.exceptions import PreventUpdate
import nidaqmx
import time
from utils.nidaq import nidaq_base_config
from utils.utils import substract_arrays


CalibrationModal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Calibration")),
                dbc.ModalBody(
                    children=[
                        dbc.Input(
                            id="weight-calibration-input",
                            placeholder="poids étalon placé sur la balance",
                        ),
                        dbc.Button(
                            "Etallonner",
                            color="info",
                            id="weight-calibration-button",
                            class_name="m-2",
                        ),
                    ],
                    class_name="text-center",
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="calibration-modal-close",
                        class_name="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="modal",
            is_open=False,
        ),
        dcc.Store(id="calibration-coeff", data=148.96158708177123),
    ]
)

# Set the sampling rate and number of samples to read
sampling_rate = 1000  # Hz
num_samples = 3000


@callback(
    Output("modal", "is_open"),
    [
        Input("calibration-modal-open", "n_clicks"),
        Input("calibration-modal-close", "n_clicks"),
    ],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@callback(
    Output("calibration-coeff", "data"),
    Input("weight-calibration-button", "n_clicks"),
    State("weight-calibration-input", "value"),
    State("zero-calibration", "data"),
    prevent_initial_call=True,
)
def set_calibration_coeff(click, value, zero_calib):
    print("--set_calibration_coeff--")
    with nidaqmx.Task() as task:
        data = substract_arrays(nidaq_base_config(task), zero_calib)

    mean_z = []

    for i in range(4, 7):
        mean_z.append((sum(data[i]) / len(data[i])) * 56.6509007)

    return
