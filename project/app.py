from components import sidebar, Footer, StartStopCalibrate

# manage logins
from flask_login import LoginManager, UserMixin, current_user

# use to config server
import warnings
import configparser
import os
import glob
import sys

# dash dependencies
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, callback, Input, Output
import dash

# other imports
import pandas as pd

module_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__))))
if module_path not in sys.path:
    sys.path.append(module_path)


ROOT_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
SRC_FOLDER = os.path.join(ROOT_FOLDER, "force_plate_app/")
ASSETS_FOLDER = os.path.join(SRC_FOLDER, "assets")

external_style_sheet = [dbc.themes.LUX]
external_style_sheet += glob.glob(os.path.join(ASSETS_FOLDER, "css") + "/*.css")

app = Dash(
    __name__,
    title="Force plate dashboard",
    external_stylesheets=external_style_sheet,
    suppress_callback_exceptions=True,
    use_pages=True,
)

server = app.server

# config the server to interact with the database
# Secret Key is used for user sessions
server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI="sqlite:///data.sqlite",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)


app.layout = html.Div(
    [
        html.Div(id="sidebar-div"),
        html.Div(
            className="page-wrapper",
            id="page-content",
            children=[dash.page_container, Footer],
        ),
        dcc.Store(id="fz-range"),
        dcc.Location(id="url"),
    ]
)


@callback(
    Output("fz-range", "data"),
    Input("range-slider", "value"),
)
def set_z_range(value):
    print(value)
    return value


@callback(
    Output("sidebar-div", "children"),
    Input("url", "pathname"),
)
def page_wrapper(pathname):
    print(pathname)
    if pathname not in ["/login", "/create_user"]:
        return sidebar
    else:
        return None


if __name__ == "__main__":
    app.run_server(port=8889, debug=True)
