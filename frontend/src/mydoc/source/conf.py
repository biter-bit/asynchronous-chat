# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys

source_encoding = 'utf-8'

sys.path.insert(0, '/home/michael/python_work/asynchronous_chat_gb/frontend')
sys.path.insert(0, '/home/michael/python_work/asynchronous_chat_gb/backend')
sys.path.insert(0, '/home/michael/python_work/asynchronous_chat_gb/')

project = 'async_chat'
copyright = '2023, mixeil'
author = 'mixeil'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
