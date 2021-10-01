#coding: utf-8

from ._version import get_versions
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

__version__ = get_versions()['version']
del get_versions
