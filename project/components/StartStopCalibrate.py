import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, ctx, dcc
from dash.exceptions import PreventUpdate
import nidaqmx
from utils.nidaq import nidaq_base_config

button_style = {"font-size": "20px"}

button1_content = "Démarrer"
button1 = dbc.Button(
    button1_content,
    id="start",
    color="success",
    class_name="ml-3",
    style=button_style,
    size="lg",
)

button2_content = "Arrêter"
button2 = dbc.Button(
    button2_content, id="end", color="danger", class_name="ml-3", style=button_style
)

button3_content = "Calibrer"
button3 = dbc.Button(
    button3_content,
    id="calibration-button",
    color="info",
    class_name="ml-3",
    style=button_style,
    n_clicks=0,
)


StartStopCalibrate = dbc.ButtonGroup([button1])


@callback(
    Output("zero-calibration", "data"),
    [
        Input("calibration-button", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def data_acquisition_start(n_clicks):
    print("start calibration")

    with nidaqmx.Task() as task:
        data = nidaq_base_config(task)

        calibration = []

        for l in data:
            mean = sum(l) / len(l)
            calibration.append(mean)

        print(calibration)

        return calibration
