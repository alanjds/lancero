from distutils.core import setup

setup(
    name = "lancero",
    version = "0.1",
    packages = ['lancero',
                'lancero.misc',
                'lancero.django',
                'lancero.django.forms'],
    zip_safe = False,
    author = "Alan Justino da Silva",
    author_email = "alan.justino[at]yahoo.com.br",
    description = "Snippets used by Lancero.com.br. Used mainly with Django",
    url = "http://github.com/alanjds/lancero",
)