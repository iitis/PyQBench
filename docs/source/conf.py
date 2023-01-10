# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from datetime import datetime
from typing import List

from pkg_resources import get_distribution

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "PyQBench"
copyright = "2022, Konrad Jałowiecki, Paulina Lewandowska, Łukasz Pawela"
author = "Konrad Jałowiecki, Paulina Lewandowska, Łukasz Pawela"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "myst_nb",
    "sphinx.ext.mathjax",
    "sphinx_math_dollar",
    "sphinxcontrib.bibtex",
    "sphinx_design",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
]

templates_path = ["_templates"]
exclude_patterns: List[str] = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_logo = "_static/logo.png"
html_css_files = ["css/custom.css"]

myst_enable_extensions = ["colon_fence", "dollarmath", "attrs_image", "amsmath", "substitution"]

myst_substitutions = {
    "version": get_distribution("pyqbench").version,
    "date": datetime.now().strftime("%Y-%m-%d"),
}

autodoc_typehints = "description"

mathjax3_config = {
    "tex": {
        "macros": {
            "PP": r"\mathcal{P}",
            "QQ": r"\mathcal{Q}",
            "proj": [r"\ketbra{#1}{#1}", 1],
            "Id": r"{\rm 1\hspace{-0.9mm}l}",
        }
    }
}

numfig = True
bibtex_bibfiles = ["references.bib"]
bibtex_default_style = "plain"

intersphinx_mapping = {
    "qiskit": ("https://qiskit.org/documentation/", None),
}

extlinks = {"qiskit_tutorials": ("https://qiskit.org/documentation/tutorials/%s", None)}
