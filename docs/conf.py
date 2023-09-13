# Configuration file for Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys

# Add the project directory to the Python path if needed (e.g., for autodoc)
# sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------
project = 'scrapemed'
author = 'Daniel Frees'

# The short X.Y version
version = '1.0.6'
# The full version, including alpha/beta/rc tags
release = '1.0.6'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # Include documentation from docstrings
    'sphinx.ext.todo',         # Enable todo items
    'sphinx.ext.viewcode',     # Add links to highlighted source code
    'sphinx.ext.githubpages',  # Publish to GitHub Pages
    'sphinx.ext.napoleon',     # Support for Google-style docstrings
    'sphinx_rtd_theme',        # ReadTheDocs theme (install with pip)
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Use the ReadTheDocs theme
html_static_path = ['_static']
#html_css_files = ['custom.css']  # You can add your own custom CSS files

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    'preamble': '',
}

# -- Options for manual page output -----------------------------------------
man_pages = [
    (master_doc, project, f'{project} Documentation', [author], 1)
]

# -- Options for Texinfo output ---------------------------------------------
texinfo_documents = [
    (master_doc, project, f'{project} Documentation', author, project, 'Data Scraper for PubMed Central.', 'Data'),
]

# -- Options for autodoc extension ------------------------------------------
# By default, autodoc generates documentation from docstrings. You can
# customize its behavior using various options.

# Example configuration for autodoc:
# autodoc_default_options = {
#     'members': True,    # Document class members (methods and attributes)
#     'undoc-members': True,  # Include members with no docstrings
#     'show-inheritance': True,  # Show base class(es) for classes
# }

# -- Options for napoleon extension -----------------------------------------
# If you're using Google-style docstrings, configure napoleon as needed.

# napoleon_google_docstring = True
# napoleon_numpy_docstring = False
# napoleon_include_init_with_doc = True
# napoleon_include_private_with_doc = False
# napoleon_include_special_with_doc = True
# napoleon_use_admonition_for_examples = False
# napoleon_use_admonition_for_notes = False
# napoleon_use_admonition_for_references = False

# -- Options for todo extension ---------------------------------------------
# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True