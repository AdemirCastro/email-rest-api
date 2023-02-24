import json
from fastapi import FastAPI

def json_to_md(json_object: dict, h1='TITULO'):
    md = f'# {h1}'
    for header, data in json_object.items():
        if 'Link' not in header:
            md += f'## {header}\n'
            if len(data) >= 0:
                for content in data:
                    if type(content) == dict:
                        for key,value in content.items():
                            md += f'**{key}**: {value}\n\n'
                        md += "\n"
                    else:
                        md+= f'{content}'
    with open("./app-doc.md", "w") as fd:
        print(md, file=fd)


def generate_documentation(app: FastAPI) -> None:
    HTML_TEMPLATE = """<!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8">
            <title>My Project - ReDoc</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
            <style>
                body {
                    margin: 0;
                    padding: 0;
                }
            </style>
            <style data-styled="" data-styled-version="4.4.1"></style>
        </head>
        <body>
            <div id="redoc-container"></div>
            <script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"> </script>
            <script>
                var spec = %s;
                Redoc.init(spec, {}, document.getElementById("redoc-container"));
            </script>
        </body>
        </html>
        """
    with open(f"./index.html", "w") as fd:
        print(HTML_TEMPLATE % json.dumps(app.openapi()), file=fd)