from os import environ
from os.path import join

GIMMEBIO_HOME = environ.get('GIMMEBIO_HOME', join(environ['HOME'], '.gimmebio'))