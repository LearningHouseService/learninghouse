#coding: utf-8

import click
import click_log

from . import logger
from .service import run


@click.command()
@click.option('--production', is_flag=True, default=False)
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=5000)
@click_log.simple_verbosity_option(logger)
def cli(**kwargs):
    logger.info('CLI provided by click (%s)', click.__version__)
    run(**kwargs)


if __name__ == '__main__':
    cli(prog_name='learninghouse')
