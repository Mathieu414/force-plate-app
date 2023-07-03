import dash
from dash import html, dash_table, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash

from utils.database import (
    db,
    conn,
    Users_tbl,
    create_users_table,
    drop_users_table,
    Users,
)

dash.register_page(__name__, path="/login")

email_input = html.Div(
    [
        dbc.Label("Email", html_for="login-email"),
        dbc.Input(type="email", id="login-email", placeholder="Entrez votre email"),
        dbc.FormText(
            "Un bout de texte avec un @ au milieu",
            color="secondary",
        ),
    ],
    className="mb-3",
)

password_input = html.Div(
    [
        dbc.Label("Mot de passe", html_for="login-password"),
        dbc.Input(
            type="password",
            id="login-password",
            placeholder="Entrez le mot de passe",
        ),
        dbc.FormText("Si vous vous en souvenez c'est encore mieux", color="secondary"),
    ],
    className="mb-3",
)

layout = html.Div(
    children=[
        html.H1("Login"),
        dbc.Form(
            [
                email_input,
                password_input,
                dbc.Button("Se connecter", color="primary", id="login-button"),
            ],
            class_name="col-6 mx-auto mt-5",
        ),
        html.P(
            ["Pas de compte ? ", dcc.Link("Se créer un compte", href="/create_user")]
        ),
        dash_table.DataTable(
            data=pd.read_sql("select * from users", conn).to_dict("records")
        ),
    ],
    className="text-center",
)


@callback(
    Output("url_login", "pathname"),
    [Input("login-button", "n_clicks")],
    [State("login-email", "value"), State("login-password", "value")],
)
def successful(n_clicks, input1, input2):
    user = Users.query.filter_by(email=input1).first()
    if user:
        if check_password_hash(user.password, input2):
            login_user(user)
            return "/success"
        else:
            pass
    else:
        pass
