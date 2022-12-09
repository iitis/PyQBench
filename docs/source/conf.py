# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from typing import List

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "PyQBench"
copyright = "2022, Konrad Jałowiecki, Paulina Lewandowska, Łukasz Pawela"
author = "Konrad Jałowiecki, Paulina Lewandowska, Łukasz Pawela"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "myst_nb", "sphinx.ext.mathjax", "sphinx_math_dollar"]

templates_path = ["_templates"]
exclude_patterns: List[str] = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

myst_enable_extensions = ["colon_fence", "dollarmath", "attrs_image"]

autodoc_typehints = "description"
