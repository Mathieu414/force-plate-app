from dash import html
import dash_bootstrap_components as dbc


def ValueCard(card_value, card_description, card_tail, card_id, height=30):
    return dbc.Card(
        class_name="text-center",
        children=dbc.CardBody(
            children=[
                html.H3(
                    className="mb-1 mt-2 card-title",
                    style={"font-size": "4.2vw"},
                    children=card_value,
                    id=card_id,
                ),
                html.H2(
                    className="card-title mb-1",
                    children=card_description,
                    style={"font-size": "2vw"},
                ),
                html.Small(
                    className="card-text",
                    children=card_tail,
                ),
            ],
            class_name="my-auto",
            style={"flex": 0},
        ),
        style={"height": str(height) + "vh"},
    )
