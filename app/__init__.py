import os
import threading
import time
import telebot
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate

from app.modules.mail.services import MailService
from core.configuration.configuration import get_app_version
from core.managers.module_manager import ModuleManager
from core.managers.config_manager import ConfigManager
from core.managers.error_handler_manager import ErrorHandlerManager
from core.managers.logging_manager import LoggingManager

# Cargar variables de entorno
load_dotenv()

# Crear las instancias
db = SQLAlchemy()
migrate = Migrate()
mail_service = MailService()

# Inicializar el diccionario de bots
bots = {}


def set_bot_handlers(bot, token):
    """Configura los manejadores para un bot dado."""

    @bot.message_handler(commands=["start"])
    def send_welcome(message):
        bot.reply_to(message, f"¡Hola! Bienvenido al Bot con token {token}")

    @bot.message_handler(commands=["help"])
    def send_help(message):
        bot.reply_to(message, f"¿Cómo puedo ayudarte con el Bot {token}?")


def start_bot(token, webhook_url):
    """Inicializa y comienza el bot para un token dado usando Webhook."""
    print(
        f"Iniciando bot con token: {token}"
    )  # Para verificar que la función se está ejecutando
    bot = telebot.TeleBot(token)
    bots[token] = bot

    # Configurar los manejadores
    set_bot_handlers(bot, token)

    # Configurar el webhook con manejo de reintentos
    retries = 5  # Número de reintentos
    for attempt in range(retries):
        try:
            bot.remove_webhook()  # Elimina cualquier webhook anterior
            time.sleep(1)  # Pausa de 1 segundo para evitar el error 429
            bot.set_webhook(url=webhook_url)  # Establece el webhook
            print(f"Webhook establecido para el bot con token {token}.")
            break  # Si tiene éxito, rompe el bucle
        except telebot.apihelper.ApiTelegramException as e:
            if e.result_json.get("error_code") == 429:  # Si es el error 429
                retry_after = int(
                    e.result_json.get("parameters", {}).get("retry_after", 1)
                )
                print(f"Error 429 recibido. Esperando {retry_after} segundos...")
                time.sleep(
                    retry_after
                )  # Espera según el tiempo recomendado por Telegram
            else:
                print(f"Error al establecer el webhook para el bot {token}: {e}")
                break  # Si es otro tipo de error, termina los reintentos


def start_bots():
    """Iniciar los bots y configurar los webhooks."""
    bot_tokens = [os.getenv("TELEGRAM_BOT_1")]  # Reemplaza con los tokens reales

    webhook_url = os.getenv(
        "WEBHOOK_URL"
    )

    for token in bot_tokens:
        # Crear un hilo para cada bot
        thread = threading.Thread(target=start_bot, args=(token, webhook_url))
        thread.daemon = True
        thread.start()


def create_app(config_name="development"):
    app = Flask(__name__)

    # Cargar la configuración según el entorno
    config_manager = ConfigManager(app)
    config_manager.load_config(config_name=config_name)

    # Inicializar SQLAlchemy y Migrate con la app
    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar módulos
    module_manager = ModuleManager(app)
    module_manager.register_modules()

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.modules.auth.models import User
        return User.query.get(int(user_id))

    # Set up logging
    # Configuración de logging
    logging_manager = LoggingManager(app)
    logging_manager.setup_logging()

    # Inicializar el manejador de errores
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
            "APP_VERSION": get_app_version(),
        }

    # Iniciar los bots cuando la app se inicie
    start_bots()

    # Crear un endpoint de webhook
    @app.route("/webhook", methods=["POST"])
    def webhook():
        json_str = request.get_data().decode("UTF-8")
        update = telebot.types.Update.de_json(json_str)
        for bot in bots.values():
            bot.process_new_updates([update])
        return "OK"

    return app


# Crear la instancia de la aplicación Flask
app = create_app()
