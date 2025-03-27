import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, no_update, ctx
import os

# Register the page with a more appropriate path
dash.register_page(__name__, path="/documentation")


# Function to read the markdown file
def read_markdown_file(markdown_file):
    with open(markdown_file, "r", encoding="utf-8") as file:
        return file.read()


# Get the path to the docs directory - adjust if needed
docs_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs", "DOCS.md"
)

# Get the path to the docs directory - adjust if needed
usage_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs", "USAGE.md"
)


# Create the layout with proper styling
layout = html.Div(
    [
        dbc.Container(
            [
                html.H1("Docs", className="text-center my-4"),
                html.Hr(),
                dcc.Markdown(
                    read_markdown_file(usage_path),
                    className="p-3 m-3",
                    style={
                        "backgroundColor": "white",
                        "padding": "20px",
                        "borderRadius": "5px",
                        "boxShadow": "0px 0px 5px lightgrey",
                    },
                    mathjax=True,
                ),
                dcc.Markdown(
                    read_markdown_file(docs_path),
                    className="p-3 m-3",
                    style={
                        "backgroundColor": "white",
                        "padding": "20px",
                        "borderRadius": "5px",
                        "boxShadow": "0px 0px 5px lightgrey",
                    },
                    mathjax=True,
                ),
            ],
            className="my-4",
        )
    ]
)
