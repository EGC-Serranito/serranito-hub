import click
import subprocess


@click.command('run:app', help="Runs the Flask app with specified parameters.")
def run_app():
    """Runs the Flask app with host 0.0.0.0, reload, and debug options."""
    click.echo(click.style("Starting Flask app with --host=0.0.0.0, --reload, --debug", fg='green'))
    try:
        subprocess.run(['flask', 'run', '--host=0.0.0.0', '--reload', '--debug'], check=True)
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"Failed to start Flask app: {e}", fg='red'))
