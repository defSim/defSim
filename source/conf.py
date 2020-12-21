# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('..'))
print(os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'defSim'
copyright = '2019-2020, Laukemper, Keijzer & Bakker'
author = 'Laukemper, Keijzer & Bakker'

# The full version, including alpha/beta/rc tags
release = 'alpha'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx_rtd_theme",
              'sphinx.ext.autodoc',
              'sphinx.ext.napoleon',
              'sphinx.ext.mathjax'
              ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

import sphinx_rtd_theme

html_theme = "sphinx_rtd_theme"

html_sidebars = {
   '**': ['globaltoc.html', 'searchbox.html'],
   'using/windows': ['windowssidebar.html', 'searchbox.html'],
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_favicon = "fig/favicon.ico"
html_logo = "fig/defSim-logo.png"
html_theme_options = {
    'logo_only': True,
    'display_version': True,
    'style_nav_header_background': '#343131'
}

# To make sure the __init__ parts of the module implementations is included
# in the docstring:
def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        return False
    return would_skip

def setup(app):
    app.connect("autodoc-skip-member", skip)
