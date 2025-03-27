from dash import html
import dash_bootstrap_components as dbc


def ValueCard(
    card_value,
    card_description,
    card_tail,
    card_id,
    height=30,
    h3_size="4.2vw",
    h2_size="2vw",
):
    return dbc.Card(
        class_name="text-center",
        children=dbc.CardBody(
            children=[
                html.H3(
                    className="mb-1 mt-2 card-title",
                    style={"fontSize": h3_size},
                    children=card_value,
                    id=card_id,
                ),
                html.H2(
                    className="card-title mb-1",
                    children=card_description,
                    style={"fontSize": h2_size},
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
