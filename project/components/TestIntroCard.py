from dash import html
import dash_bootstrap_components as dbc

TestIntroCard = dbc.Card([
    dbc.CardBody([

        html.H2(["Dashboard Plateforme de force"],
                className="card-title"),
        html.H6(
            "Aide à l'analyse de mouvement pour les sportifs de haut niveau", className="card-subtitle mb-2 text-body-secondary"),
        html.P(["Ce dashboard a pour fonction d'automatiser l'analyse des test et des séances de Force au CNSNMM. Elle fonctionne en lien avec les plateformes Kistler détenues par le CNSNMM, et avec la connectique adaptée.",
                ], className="card-text"),


        html.P(["Reportez-vous à Jonas Forot en cas de problème.",
                ], className="card-text"),

    ])

])
