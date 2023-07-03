import dash
from dash import html, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc

import pandas as pd

df = pd.DataFrame()

collection = None

dash.register_page(__name__, path="/libre")

form = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Label("Prénom", html_for="first-name-input"),
                dbc.Input(
                    type="text",
                    id="first-name-input",
                    placeholder="Entrez le prénom",
                ),
            ],
            width=6,
        ),
        dbc.Col(
            [
                dbc.Label("Nom", html_for="last-name-input"),
                dbc.Input(
                    type="text",
                    id="last-name-input",
                    placeholder="Entrez le nom",
                ),
            ],
            width=6,
        ),
    ],
    className="g-3 mb-3",
)

layout = html.Div(
    children=[
        html.Div(
            dash_table.DataTable(
                id="data-table",
                data=df.to_dict("records"),
                columns=[{"id": p, "name": p} for p in df if p != "_id"],
            ),
            className="col-8 mx-auto",
        ),
        html.Div(
            [
                form,
                dbc.Button(
                    id="add-user",
                    children=[
                        html.I(className="fas fa-plus"),
                        "Ajouter un utilisateur",
                    ],
                ),
            ],
            className="text-center col-6 mx-auto m-5 gap-2",
        ),
    ],
)


@callback(
    Output("data-table", "data"),
    Input("add-user", "n_clicks"),
    State("first-name-input", "value"),
    State("last-name-input", "value"),
    prevent_initial_call=True,
)
def add_user(clicks, first_name, last_name):
    if first_name is not None and last_name is not None:
        collection.insert_one({"firstName": first_name, "lastName": last_name})

        df = pd.DataFrame(list(collection.find()))

        # Convert id from ObjectId to string so it can be read by DataTable
        df["_id"] = df["_id"].astype(str)

        print(df)

        data = df.to_dict("records")

        return data
