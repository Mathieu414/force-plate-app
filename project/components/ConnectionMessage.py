import dash_bootstrap_components as dbc
from dash import html


def ConnectionAlert(connection_status):
    """
    Creates an alert component that shows connection status
    Args:
        connection_status (bool): True if connected, False if disconnected
    """
    if connection_status:
        return html.Div(
            [
                dbc.Alert(
                    "Plateforme de Force connectée",
                    color="success",
                    className="m-3",
                )
            ]
        )
    else:
        return html.Div(
            [
                dbc.Alert(
                    [
                        "Plateforme de Force déconnectée. Veuillez réessayer",
                    ],
                    color="danger",
                    className="m-3",
                )
            ]
        )
