import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, callback

SessionPageInfoModal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Consignes")),
        dbc.ModalBody(
            children=[
                html.P(
                    [
                        "1. Dans un premier temps, veillez à bien vérifier si la configation Fzi correspond à la configuration de la machine en appuyant sur : ",
                        html.I(className="fa fa-gear"),
                    ]
                ),
                html.P(
                    "2. Appuyez sur le boutton 'Start'. La phase de pesée commence."
                ),
                html.P(
                    "3. Montez sur la plateforme avec vos poids, et attendez le signal de fin de pesée : "
                ),
                html.Img(
                    src="/assets/images/sessionStart.png",
                    alt="Box Selection Tool",
                    style={
                        "max-width": "50%",
                        "height": "auto",
                        "margin": "0 0 10px 0",
                    },
                ),
                html.P("Vous pouvez réaliser votre séance. 💪"),
                html.Hr(),
                html.P(
                    [
                        "Pour réinitaliser votre poids"
                        " par exemple au milieu d'une séance si vous changez de charge : ",
                        html.Ul(
                            [
                                html.Li("Arrêtez la session"),
                                html.Li(
                                    [
                                        "Puis appuyez sur ce boutton : ",
                                        html.I(className="fa fa-refresh"),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
                html.Hr(),
                html.P(
                    [
                        "Pour réinitaliser vos données, appuyez sur ce boutton : ",
                        html.I(className="fa fa-trash-can"),
                    ]
                ),
            ]
        ),
        dbc.ModalFooter(dbc.Button("Fermer", id="close-info-modal", n_clicks=0)),
    ],
    id="info-modal",
    is_open=False,
)

FreePageInfoModal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Consignes - Usage Simple")),
        dbc.ModalBody(
            children=[
                html.P(
                    [
                        "1. Dans un premier temps, veillez à bien vérifier si la configation Fzi correspond à la configuration de la machine en appuyant sur : ",
                        html.I(className="fa fa-gear"),
                    ]
                ),
                html.P("2. Appuyez sur le boutton 'Start', puis amusez-vous !"),
                html.P(
                    """Arrêtez la séance à tout moment en appuyant sur le boutton Stop. 
                    Vous pouvez aussi réinitialiser les données en appuyant sur le boutton Reset."""
                ),
                html.P("L'export des données est décomposé sur les 4 capteurs."),
                html.P(
                    "Pour avoir des valeurs pour une zone de données spécifique, utilisez le boutton de box selection :"
                ),
                html.Img(
                    src="/assets/images/boxSelectToolBar.png",
                    alt="Box Selection Tool",
                    style={"max-width": "100%", "height": "auto", "margin": "10px 0"},
                ),
            ]
        ),
        dbc.ModalFooter(dbc.Button("Fermer", id="close-info-modal", n_clicks=0)),
    ],
    id="info-modal",
    is_open=False,
)


@callback(
    Output("info-modal", "is_open"),
    [Input("open-info-modal", "n_clicks"), Input("close-info-modal", "n_clicks")],
    [State("info-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
