from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

# Project --------------------------------------------------------------

project = "itsdangerous"
copyright = "2011 Pallets Team"
author = "Pallets Team"
release, version = get_version("itsdangerous")

# General --------------------------------------------------------------

master_doc = "index"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "pallets_sphinx_themes"]
intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}

# HTML -----------------------------------------------------------------

html_theme = "flask"
html_theme_options = {"index_sidebar_logo": False}
html_context = {
    "project_links": [
        ProjectLink("Donate to Pallets", "https://palletsprojects.com/donate"),
        ProjectLink("Website", "https://palletsprojects.com/p/itsdangerous/"),
        ProjectLink("PyPI releases", "https://pypi.org/project/itsdangerous/"),
        ProjectLink("Source Code", "https://github.com/pallets/itsdangerous/"),
        ProjectLink("Issue Tracker", "https://github.com/pallets/itsdangerous/issues/"),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}
html_static_path = ["_static"]
html_logo = "_static/itsdangerous-logo-sidebar.png"
html_title = "itsdangerous Documentation ({})".format(version)
html_show_sourcelink = False

# LaTeX ----------------------------------------------------------------

latex_documents = [
    (master_doc, "itsdangerous-{}.tex".format(version), html_title, author, "manual")
]
