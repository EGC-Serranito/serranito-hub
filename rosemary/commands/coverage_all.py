import click
import subprocess


@click.command('coverage:all', help="Runs pytest coverage for all the project and creates a report.")
def coverage_all():
    """uns pytest coverage for all the projects and creates a report."""
    click.echo(click.style("Starting coverage analisys. Please stay tunned", fg='green'))
    click.echo(click.style("Remember that you should have the app running in order to calculate coverage properly", fg='green'))
    try:
        subprocess.run(['pytest', '--cov', '--cov-report', 'html'], check=True)
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"Error running coverage: {e}", fg='red'))
