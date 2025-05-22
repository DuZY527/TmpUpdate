from fastapi import FastAPI, applications
from fastapi.openapi.docs import get_swagger_ui_html


def swagger_monkey_patch(*args, **kwargs):
    """
    Wrap the function which is generating the HTML for the /docs endpoint and
    overwrite the default values for the swagger js and css.
    """
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.staticfile.org/swagger-ui/5.0.0/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.org/swagger-ui/5.0.0/swagger-ui.min.css")

applications.get_swagger_ui_html = swagger_monkey_patch

app = FastAPI()

