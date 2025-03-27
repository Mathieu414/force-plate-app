import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
from components.Sliders import sliders_content
from utils.nidaq import SessionDataAcquisition


def parameters_content(daq: SessionDataAcquisition):
    return html.Div(
        [
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "Seuil de regroupement des zones basses :"
                                    ),
                                    dbc.Input(
                                        id="low-peak-group-threshold",
                                        placeholder="Valeur...",
                                        type="number",
                                        value=daq.low_peak_group_threshold,
                                    ),
                                ],
                                className="mb-2",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "Seuil de largeur de détection des pics :",
                                    ),
                                    dbc.Input(
                                        id="high-peak-width-threshold",
                                        placeholder="Valeur...",
                                        type="number",
                                        value=daq.high_peak_width_threshold,
                                    ),
                                ],
                                className="mb-2",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "Largeur de la fenêtre de detection du poids :",
                                    ),
                                    dbc.Input(
                                        id="weight-window-size",
                                        placeholder="Valeur...",
                                        type="number",
                                        value=daq.weight_window_size,
                                    ),
                                ],
                                className="mb-2",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "Seuil supérieur de variance pour la détection du poids :",
                                    ),
                                    dbc.Input(
                                        id="weight-std-threshold",
                                        placeholder="Valeur...",
                                        type="number",
                                        value=daq.weight_std_threshold,
                                    ),
                                ],
                                className="mb-2",
                            ),
                        ],
                        title="Paramètres additionels",
                    ),
                ],
                start_collapsed=True,
            )
        ],
        className="mt-4",
    )


def ParametersModal(daq):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Paramètres")),
            dbc.ModalBody(children=[sliders_content, parameters_content(daq)]),
        ],
        id="parameters-modal",
        is_open=False,
    )


@callback(
    Output("parameters-modal", "is_open"),
    Input("open-parameters-modal", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_modal(n1):
    return True
