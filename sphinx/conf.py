import sphinx_rtd_theme

from confu import __version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

source_suffix = '.rst'
master_doc = 'index'

project = u'Confu: Ninja-based configuration system'
copyright = u'2017, Georgia Institute of Technology'

version = __version__
release = __version__

pygments_style = 'sphinx'
autoclass_content = 'both'

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
