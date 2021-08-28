from jinja2 import Environment, PackageLoader, select_autoescape
from typing import List
from twitbooks.sync import JsonBodySyncValue


def render(res: List[JsonBodySyncValue]) -> str:
    env = Environment(
        loader=PackageLoader("twitbooks"),
        autoescape=select_autoescape()
    )
    template = env.get_template("books.html")
    return template.render(results=res)
