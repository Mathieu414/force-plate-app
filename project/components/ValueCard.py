from dash import html


def ValueCard(card_header, card_body, card_tail, class_name=""):
    return html.Div(className="col-6" + class_name,
                    children=[
                        html.Div(className="card", children=[
                            html.Div(className="card-body", children=[
                                html.Div(className="card-info text-center",
                                 children=[html.H3(className="mb-1 mt-2 card-title mb-2",
                                                   style={"font-size": "4.2vw"}, children=[card_header]),
                                           html.H2(className="card-title mb-1",
                                                   children=[card_body], style={"font-size": "2vw"}),
                                           html.Small(
                                     className="card-text", children=[card_tail]
                                 )
                                 ])
                            ])
                        ])
                    ])
