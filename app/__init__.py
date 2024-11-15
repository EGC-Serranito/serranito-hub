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
import requests

# Load environment variables
load_dotenv()

# Create the instances
db = SQLAlchemy()
migrate = Migrate()
mail_service = MailService()
scheduler = APScheduler()


# Function to send a message to the bot
def send_messages_bot(bot_token, chat_id, features):
    message = (
        "*🔍 Features found:*\n\n"
        + "\n".join([f"• *{feature}*" for feature in features])
        + "\n\n"
        + "*For more information about this bot, visit:* \n"
        + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print(f"Message successfully sent to {chat_id}.")
        else:
            print(f"Error sending message: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")


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
            for bot_token in treenode_bot_dict[0].get("children", []):
                BOT_TOKEN = bot_token.get("name")
                for chat_id in bot_token.get("children", [])[0].get("children", []):
                    CHAT_ID = chat_id.get("name")
                    features = [
                        node.get("name")
                        for node in chat_id.get("children", [])[0]
                        .get("children", [])[1]
                        .get("children", [])
                    ]
                    send_messages_bot(BOT_TOKEN, CHAT_ID, features)
    except Exception as e:
        # Capture any exception and display it in the console
        print(f"Error executing the bot task: {e}")


# Schedule the job to execute every 9 seconds
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


# Initialize the app
app = create_app()
