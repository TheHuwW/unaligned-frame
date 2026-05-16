import os
import sys

# Ensure Sphinx can find the source code in the src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

project = 'Unaligned Frame'
copyright = '2026, Huw Trefor Williams'
author = 'Huw Trefor Williams'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',     # Core library for generating docs from docstrings
    'sphinx.ext.napoleon',    # Support for Google and NumPy style docstrings
    'sphinx.ext.viewcode',    # Add links to highlighted source code
    'sphinx_rtd_theme',       # Use the Read the Docs theme
]

# Mock heavy dependencies so they don't need to be installed for the doc build
autodoc_mock_imports = ["pandas", "numpy"]

# Improve readability of type hints
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True  # Pulls the __init__ docstring into the class doc
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
