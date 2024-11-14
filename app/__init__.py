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


# Función que envia el mensaje al bot
def send_messages_bot(bot_token, chat_id, features):
    message = (
        "*🔍 Características encontradas:*\n\n"
        + "\n".join([f"• *{feature}*" for feature in features])
        + "\n\n"
        + "*Para más información sobre este bot, visita:* \n"
        + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"Mensaje enviado a {chat_id} exitosamente.")
        else:
            print(f"Error al enviar mensaje: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")


# Función que procesará el árbol de nodos
def bot_task(app):
    with app.app_context():  # Establecer el contexto de la app
        start_bot_task()


def start_bot_task():
    """Inicia la tarea del bot procesando el árbol de nodos y enviando mensajes."""

    # Importar el modelo de TreeNodeBot desde el módulo correspondiente
    from app.modules.botintegration.models import TreeNodeBot

    # Obtener nodos del árbol desde la base de datos
    treenode_bot = TreeNodeBot.query.all()  # Aquí directamente consultas los modelos

    # Convertir a diccionarios si hay datos
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
        # Capturar cualquier excepción y mostrarla en la consola
        print(f"Error en la ejecución de la tarea del bot: {e}")


# Configurar el job para ejecutar cada 9 segundos
@scheduler.task("cron", id="bot_task", hour=20, minute=0)
def scheduled_task():
    bot_task(app)


# Crear la aplicación Flask
def create_app(config_name="development"):
    app = Flask(__name__)

    # Load configuration according to environment
    config_manager = ConfigManager(app)
    config_manager.load_config(config_name=config_name)

    # Inicializar SQLAlchemy y Migrate con la app
    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar módulos
    module_manager = ModuleManager(app)
    module_manager.register_modules()

    # Registrar login manager
    from flask_login import LoginManager

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.modules.auth.models import User

        return User.query.get(int(user_id))

    # Configurar logging
    logging_manager = LoggingManager(app)
    logging_manager.setup_logging()

    # Inicializar el gestor de errores
    error_handler_manager = ErrorHandlerManager(app)
    error_handler_manager.register_error_handlers()

    # Inicializar el servicio de correo
    mail_service.init_app(app)

    # Inyectar variables de entorno en el contexto de Jinja
    @app.context_processor
    def inject_vars_into_jinja():
        return {
            "FLASK_APP_NAME": os.getenv("FLASK_APP_NAME"),
            "FLASK_ENV": os.getenv("FLASK_ENV"),
            "DOMAIN": os.getenv("DOMAIN", "localhost"),
            "APP_VERSION": get_app_version(),  # Iniciar el scheduler
        }

    # Solo iniciar el scheduler si no está en ejecución
    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.start()

    return app


# Inicializar la app
app = create_app()
