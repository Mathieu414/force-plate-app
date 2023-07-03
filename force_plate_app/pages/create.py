import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

# database
from utils.database import Users_tbl, engine

# manage password hashing
from werkzeug.security import generate_password_hash

import sqlite3

conn = sqlite3.connect("data.sqlite")

dash.register_page(__name__, path="/create_user")


email_input = dbc.Row(
    [
        dbc.Label("Email", html_for="create-email", width=2),
        dbc.Col(
            dbc.Input(type="email", id="create-email", placeholder="Entez votre email"),
            width=10,
        ),
    ],
    className="mb-3",
)

password_input = dbc.Row(
    [
        dbc.Label("Mot de passe", html_for="create-password", width=2),
        dbc.Col(
            dbc.Input(
                type="password",
                id="create-password",
                placeholder="Entrez votre mot de passe",
            ),
            width=10,
        ),
    ],
    className="mb-3",
)

layout = html.Div(
    children=[
        html.H1("Création de compte"),
        dbc.Form(
            [
                email_input,
                password_input,
                dbc.Button("Créer", color="primary", id="create-submit"),
            ],
            class_name="col-6 mx-auto mt-5",
        ),
        dcc.Location(id="create-url", refresh=True),
    ],
    className="text-center",
)


@callback(
    Output("create-url", "pathname"),
    [Input("create-submit", "n_clicks")],
    [State("create-email", "value"), State("create-password", "value")],
)
def insert_users(n_clicks, em, pw):
    if pw is not None and em is not None:
        hashed_password = generate_password_hash(pw)
        ins = Users_tbl.insert().values(
            password=hashed_password,
            email=em,
        )
        with engine.connect() as conn:
            conn.execute(ins)
            conn.commit()
        return "/login"
    else:
        return None
