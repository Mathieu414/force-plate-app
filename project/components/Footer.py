from dash import html


Footer = html.Footer(
    html.Div(
        html.H6(
            [
                "©2023, Developed By ",
                html.A("Mathieu Perrin", style={"color": "#0084d6"}),
            ]
        )
    )
)
