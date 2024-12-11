from app import db, create_app
import click
import os
from flask.cli import with_appcontext
from rosemary.commands.db_seed import get_module_seeders


@click.command('populate:external_db', help="Populate an external mysqldatabase using local seeders.")
@with_appcontext
def populate_external_db():
    """Populate an external Mysql database using seeders."""

    app = create_app(config_name='externalDB')
    with app.app_context():

        db.drop_all()
        db.create_all()
        blueprints_module_path = os.path.join(os.getenv('WORKING_DIR', ''), 'app/modules')
        seeders = get_module_seeders(blueprints_module_path)
        success = True
        click.echo(click.style("Please make sure you configure your env variables properly", fg='yellow'))
        click.echo(click.style("Take into account that this does not affect app image uploads folder", fg='yellow'))
        click.echo(click.style("Seeding data for all modules...", fg='green'))
        click.echo(click.style(f"Connecting to database: {app.config['SQLALCHEMY_DATABASE_URI']}", fg='blue'))
        for seeder in seeders:
            try:
                seeder.run()
                click.echo(click.style(f'{seeder.__class__.__name__} performed.', fg='blue'))
            except Exception as e:
                click.echo(click.style(f'Error running seeder {seeder.__class__.__name__}: {e}', fg='red'))
                click.echo(click.style(f'Rolled back the transaction of {seeder.__class__.__name__} to keep the session '
                                    f'clean.',
                                    fg='yellow'))

                success = False
                break

        if success:
            click.echo(click.style('External database populated with test data.', fg='green'))
