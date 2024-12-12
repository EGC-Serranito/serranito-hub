import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from app.modules.mail.services import MailService
from core.configuration.configuration import get_app_version
from core.managers.module_manager import ModuleManager
from core.managers.config_manager import ConfigManager
from core.managers.error_handler_manager import ErrorHandlerManager
from core.managers.logging_manager import LoggingManager
from app.modules.botintegration.features import FeatureService

featureService = FeatureService()

# Load environment variables
load_dotenv()

# Create the instances
db = SQLAlchemy()
migrate = Migrate()
mail_service = MailService()
scheduler = APScheduler()


# Function to process the node tree
def bot_task(app):
    with app.app_context():  # Set the app context
        start_bot_task()


def start_bot_task():
    """Starts the bot task by processing the node tree and sending messages."""

    # Import the TreeNodeBot model from the corresponding module
    from app.modules.botintegration.models import TreeNodeBot

    # Fetch nodes from the tree in the database
    treenode_bot = TreeNodeBot.query.all()  # Directly query the models here

    # Convert to dictionaries if there is data
    treenode_bot_dict = (
        [node.to_dict() for node in treenode_bot] if treenode_bot else []
    )
    try:
        if treenode_bot_dict:
            # Iterate through each bot token in the dictionary, check if it has 'children'
            for bot_token in treenode_bot_dict[0].get("children", []):
                BOT_TOKEN = bot_token.get("name")
                # Proceed only if the bot_token has a name
                if BOT_TOKEN:
                    # Iterate through chat_ids for the bot_token, check if 'children' exist
                    for chat_id in bot_token.get("children", [])[0].get("children", []):
                        CHAT_ID = chat_id.get("name")
                        # Proceed only if the chat_id has a name
                        if CHAT_ID:
                            # Safely navigate through the nested structure to get features
                            features = []

                            # Check if the first level of children exists
                            first_children = chat_id.get("children", [])
                            if len(first_children) > 0:
                                # Check if the second level of children exists
                                second_children = first_children[0].get("children", [])
                                if len(second_children) > 1:
                                    # Check if the third level of children exists
                                    third_children = second_children[1].get("children", [])
                                    # Now, process the third level
                                    for node in third_children:
                                        # Add an additional check to ensure 'name' exists in the node
                                        if node.get("name"):
                                            features.append(node.get("name"))
                            # Ensure features is a list (it should always be, but we guard against empty cases)
                            if features:
                                domain = os.getenv("DOMAIN", "localhost")  # Default to 'localhost' if DOMAIN is missing
                                url = featureService.transform_to_full_url(domain)
                                # Send features only if we have them
                                featureService.send_features_bot(BOT_TOKEN, CHAT_ID, features, url)
    except Exception as e:
        # Capture any exception and display it in the console
        print(f"Error executing the bot task: {e}")


@scheduler.task("cron", id="bot_task", hour=20, minute=0)
def scheduled_task():
    bot_task(app)


# Create the Flask application
def create_app(config_name="development"):
    app = Flask(__name__)

    # Load configuration according to environment
    config_manager = ConfigManager(app)
    config_manager.load_config(config_name=config_name)

    # Initialize SQLAlchemy and Migrate with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register modules
    module_manager = ModuleManager(app)
    module_manager.register_modules()

    # Register login manager
    from flask_login import LoginManager

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.modules.auth.models import User

        return User.query.get(int(user_id))

    # Configure logging
    logging_manager = LoggingManager(app)
    logging_manager.setup_logging()

    # Initialize the error manager
    error_handler_manager = ErrorHandlerManager(app)
    error_handler_manager.register_error_handlers()

    # Initialize the mail service
    mail_service.init_app(app)

    # Inject environment variables into the Jinja context
    @app.context_processor
    def inject_vars_into_jinja():
        return {
            "FLASK_APP_NAME": os.getenv("FLASK_APP_NAME"),
            "FLASK_ENV": os.getenv("FLASK_ENV"),
            "DOMAIN": os.getenv("DOMAIN", "localhost"),
            "APP_VERSION": get_app_version(),  # Start the scheduler
        }

    # Only start the scheduler if it is not running
    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.start()

    return app


app = create_app()
