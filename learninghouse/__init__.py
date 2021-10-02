#coding: utf-8

import logging
from ._version import get_versions


logging.basicConfig()
logger = logging.getLogger(__name__)

__version__ = get_versions()['version']
del get_versions
