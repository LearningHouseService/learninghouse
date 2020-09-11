import click

from .service import run

@click.command()
@click.option('--production', is_flag=True, default=False)
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=5000)
def cli(**kwargs):
    run(**kwargs)

if __name__ == '__main__':
    cli(prog_name='learninghouse')