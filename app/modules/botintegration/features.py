import requests
import yaml
import json
import os
from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from antlr4.error.ErrorListener import ErrorListener
import tempfile


class CustomErrorListener(ErrorListener):
    """
    Listener personalizado para capturar errores de sintaxis.
    """
    def __init__(self):
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"Line {line}:{column} - {msg}")


class FeatureService:
    @staticmethod
    def load_yaml_file(file_path):
        """
        Carga un archivo YAML y devuelve su contenido.

        :param file_path: Ruta del archivo YAML.
        :return: Datos cargados del archivo YAML.
        :raises: FileNotFoundError, yaml.YAMLError si hay problemas al cargar el archivo.
        """
        try:
            with open(file_path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            raise
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            raise

    @staticmethod
    def find_bot_token(bot_name, bottokens_data):
        """
        Busca y obtiene el token de un bot en los datos YAML.

        :param bot_name: Nombre del bot.
        :param bottokens_data: Datos cargados del archivo YAML.
        :return: Nombre de la variable de entorno del token del bot.
        :raises: ValueError si el bot no se encuentra o la configuración es inválida.
        """
        bot_entry = next(
            (
                entry
                for entry in bottokens_data.get("bottokens", [])
                if entry["name"] == bot_name
            ),
            None,
        )

        if not bot_entry:
            raise ValueError(f"Bot name '{bot_name}' not found in bottokens data.")

        return bot_entry.get("token")

    @staticmethod
    def get_environment_variable(var_name):
        """
        Obtiene el valor de una variable de entorno.

        :param var_name: Nombre de la variable de entorno.
        :return: Valor de la variable de entorno.
        :raises: ValueError si la variable no existe o está vacía.
        """
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Environment variable '{var_name}' not found or empty.")
        return value

    @staticmethod
    def transform_to_full_url(url):
        """
        Asegura que una URL tenga el esquema correcto (http o https).

        :param url: URL a formatear.
        :return: URL con esquema completo.
        """
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        return url

    def load_messages(self, file_path="app/modules/botintegration/assets/messages.yaml"):
        """
        Carga un archivo YAML con la configuración de mensajes.

        :param file_path: Ruta del archivo YAML.
        :return: Datos cargados del archivo YAML.
        """
        return self.load_yaml_file(file_path)

    def get_bot_token(
        self, bot_name, bottokens_path="app/modules/botintegration/assets/bottokens.yaml"
    ):
        """
        Obtiene el token de un bot específico a partir de los datos en bottokens.yaml y variables de entorno.

        :param bot_name: Nombre del bot (por ejemplo, "@uvlhub-telegram1").
        :param bottokens_path: Ruta al archivo YAML con las configuraciones de los bots.
        :return: Token del bot como cadena.
        :raises: FileNotFoundError, KeyError o ValueError si ocurre algún problema.
        """
        try:
            # Cargar datos del archivo YAML
            bottokens_data = self.load_yaml_file(bottokens_path)

            # Buscar el token del bot
            token_var = self.find_bot_token(bot_name, bottokens_data)

            # Obtener el valor de la variable de entorno
            return self.get_environment_variable(token_var)
        except Exception as e:
            print(f"Unexpected error while fetching bot token: {e}")
            raise

    def send_features_bot(self, bot_token, chat_id, features, BASE_URL):
        """
        :param bot_token: Token del bot de Telegram.
        :param chat_id: ID del chat de Telegram al que enviar los mensajes.
        :param features: Lista de características para las cuales enviar mensajes.
        :param user_data: Diccionario con los datos del usuario necesarios para formatear los mensajes.
        """
        bot_token = self.get_bot_token(bot_token)
        BASE_URL = self.transform_to_full_url(BASE_URL)
        messages_config = self.load_messages()
        messages = messages_config.get("messages", {})

        for feature in features:
            match feature:
                case "AUTH":
                    from app.modules.profile.models import UserProfile
                    from app.modules.auth.models import User

                    message_template = messages.get("AUTH", {}).get("message", "")
                    from app.modules.botintegration.models import TreeNode

                    tree_node = TreeNode.query.filter(TreeNode.name == chat_id).first()

                    user = User.query.get(tree_node.user_id)
                    user_profile = UserProfile.query.filter_by(
                        user_id=tree_node.user_id
                    ).first()
                    user_data = {
                        "email": user.email,
                        "name": user_profile.name,
                        "surname": user_profile.surname,
                        "orcid": user_profile.orcid,
                    }
                    formatted_message = message_template.format(**user_data)
                case "DATASET":
                    from app.modules.dataset.models import DSMetaData, DataSet
                    from app.modules.hubfile.services import HubfileService
                    from app.modules.botintegration.models import TreeNode
                    from flask import current_app, jsonify, make_response
                    import os

                    message_template = messages.get("DATASET", {}).get("message", "")
                    tree_node = TreeNode.query.filter(TreeNode.name == chat_id).first()

                    datasets = (
                        DataSet.query.join(DSMetaData)
                        .filter(
                            DataSet.user_id == tree_node.user_id,
                            DSMetaData.dataset_doi.isnot(None),
                        )
                        .order_by(DataSet.created_at.desc())
                        .all()
                    )
                    list_content = ""

                    for d in datasets:
                        title = d.ds_meta_data.title
                        description = d.ds_meta_data.description
                        publication_type = d.ds_meta_data.publication_type.name.replace("_", " ").title()
                        doi = d.get_uvlhub_doi()

                        # Dataset Header
                        list_content += f"🔹 *Title*: {title}\n"
                        list_content += f"📄 *Description*: {description}\n"
                        list_content += f"📚 *Publication Type*: {publication_type}\n"
                        list_content += f"🌐 *DOI*: [{doi}]({doi})\n\n"

                        for feature_model in d.feature_models:
                            for file in feature_model.files:
                                list_content += f"🔸 *File*: {file.name}\n"
                                file_service = HubfileService()
                                file = file_service.get_or_404(file.id)
                                filename = file.name

                                directory_path = (
                                    f"uploads/user_{file.feature_model.data_set.user_id}/"
                                    f"dataset_{file.feature_model.data_set_id}/"
                                )
                                parent_directory_path = os.path.dirname(current_app.root_path)
                                file_path = os.path.join(parent_directory_path, directory_path, filename)

                                try:
                                    if os.path.exists(file_path):
                                        with open(file_path, "r") as f:
                                            content = f.read()

                                        response = jsonify({"success": True, "content": content})
                                        response = make_response(response)

                                        if response.status_code == 200:
                                            data = response.get_json()
                                            file_content = data.get("content", "")
                                            if file_content:
                                                list_content += "\n👨‍💻 *File Content (UVL)*:\n"
                                                list_content += f"\n```uvl\n{file_content[:500]}\n```\n"
                                            else:
                                                list_content += "\n*Content not available.*\n"
                                        else:
                                            list_content += f"\n(Response code: {response.status_code})\n"
                                    else:
                                        list_content += "\n*⚠️ File not found.*\n"

                                except Exception as e:
                                    list_content += f"\n⚠️ *Error occurred while processing the file:* {str(e)}\n"

                                url_download = f"{BASE_URL}/file/download/{file.id}"
                                list_content += f"📥 *Download File*: {url_download}\n\n"
                    user_data = {"datasets": list_content}
                    formatted_message = message_template.format(**user_data)
                case "FLAMAPY":
                    message_template = messages.get("FLAMAPY", {}).get("message", "")
                    self.send_messages_flamapy(bot_token, chat_id)
                    formatted_message = message_template
                case "FAKENODO":
                    data = {"status": "success", "message": "Connected to Fakenodo API"}
                    user_data = {"connection": data.get("message", "No conection")}
                    message_template = messages.get("FAKENODO", {}).get("message", "")
                    formatted_message = message_template.format(**user_data)
                case "HUBSTATS":
                    from app.modules.dataset.services import DataSetService
                    from app.modules.featuremodel.services import FeatureModelService
                    dataset_service = DataSetService()
                    feature_model_service = FeatureModelService()

                    datasets_counter = dataset_service.count_synchronized_datasets()
                    feature_models_counter = feature_model_service.count_feature_models()

                    total_dataset_downloads = dataset_service.total_dataset_downloads()
                    total_feature_model_downloads = feature_model_service.total_feature_model_downloads()

                    total_dataset_views = dataset_service.total_dataset_views()
                    total_feature_model_views = feature_model_service.total_feature_model_views()

                    data = {
                        "datasets_counter": datasets_counter,
                        "feature_models_counter": feature_models_counter,
                        "total_dataset_downloads": total_dataset_downloads,
                        "total_feature_model_downloads": total_feature_model_downloads,
                        "total_dataset_views": total_dataset_views,
                        "total_feature_model_views": total_feature_model_views,
                    }

                    # Get the message template
                    message_template = messages.get("HUBSTATS", {}).get("message", "")

                    # Format the message using the data
                    formatted_message = message_template.format(**data)
                case _:
                    print(
                        f"Feature {feature} no encontrada en la configuración de mensajes."
                    )
                    continue
            try:
                self.send_message_bot(bot_token, chat_id, feature, formatted_message)
            except KeyError as e:
                print(
                    f"Error formateando el mensaje para la característica {feature}: Faltan datos {e}"
                )

    @staticmethod
    def validate_uvl_model(uvl_text):
        """
        Valida un modelo UVL y devuelve el resultado como texto.
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".uvl") as temp_file:
                temp_file.write(uvl_text.encode("utf-8"))
                temp_path = temp_file.name

            try:
                UVLReader(temp_path).transform()
                return "Valid Model"
            except Exception as e:
                return f"Error in the validation of the model: {str(e)}"
        except Exception as e:
            return f"General error: {str(e)}"

    @staticmethod
    def handle_telegram_webhook(bot_token):
        """
        Verifica y elimina un webhook activo en Telegram.
        """
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        webhook_info = response.json()

        if webhook_info["result"]["url"]:
            delete_webhook_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
            delete_response = requests.get(delete_webhook_url, timeout=10)
            if delete_response.status_code == 200:
                print("Webhook eliminado con éxito.")
            else:
                print(f"Error al eliminar el webhook: {delete_response.text}")

    @staticmethod
    def get_telegram_updates(bot_token, last_update_id=None):
        """
        Obtiene actualizaciones del bot de Telegram.
        """
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        if last_update_id:
            url += f"?offset={last_update_id + 1}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("result", [])
        print(f"Error al obtener actualizaciones: {response.text}")
        return []

    @staticmethod
    def respond_to_telegram_message(bot_token, chat_id, message_id, response_text):
        """
        Responde a un mensaje en Telegram.
        """
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": response_text,
            "reply_to_message_id": message_id,
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print(f"Respondido al mensaje {message_id} en el chat {chat_id}")
        else:
            print(f"Error al responder al mensaje {message_id}: {response.text}")

    @staticmethod
    def get_discord_messages(bot_token, chat_id):
        """
        Obtiene mensajes recientes de un canal de Discord.
        """
        url = f"https://discord.com/api/v10/channels/{chat_id}/messages"
        headers = {"Authorization": f"Bot {bot_token}"}
        params = {"limit": 10}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        print(f"Error al obtener los mensajes: {response.status_code}")
        return []

    @staticmethod
    def respond_to_discord_message(bot_token, chat_id, message_id, response_text):
        """
        Responde a un mensaje en Discord.
        """
        url = f"https://discord.com/api/v10/channels/{chat_id}/messages"
        headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json",
        }
        data = {
            "content": response_text,
            "message_reference": {"message_id": message_id},
        }
        response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Respondido al mensaje {message_id} en el chat {chat_id}")
        else:
            print(f"Error al responder al mensaje {message_id}: {response.text}")

    def send_messages_flamapy(self, bot_token, chat_id):
        """
        Procesa mensajes de Telegram o Discord y responde a cada uno.
        """
        if len(bot_token.split(":")) == 2 and not len(bot_token) == 64:
            self.handle_telegram_webhook(bot_token)
            updates = self.get_telegram_updates(bot_token)

            for update in updates:
                chat_id_messages = update["message"]["chat"]["id"]
                message_id = update["message"]["message_id"]
                uvl_message = update["message"].get("text", "Mensaje sin texto")

                if int(chat_id) == int(chat_id_messages):
                    response_text = self.validate_uvl_model(uvl_message)
                    self.respond_to_telegram_message(
                        bot_token, chat_id, message_id, response_text
                    )
        else:
            messages = self.get_discord_messages(bot_token, chat_id)

            for message in messages:
                if not message["author"].get("bot", False):
                    response_text = self.validate_uvl_model(message["content"])
                    self.respond_to_discord_message(
                        bot_token, chat_id, message["id"], response_text
                    )

    @staticmethod
    def format_message(feature, formatted_message):
        """
        Formats a message to be sent.
        """
        return (
            f"Message for {feature}:\n{formatted_message}\n\n"
            + "*For more information about this bot, visit:* \n"
            + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)"
        )

    @staticmethod
    def split_message(message, limit=2000):
        """
        Divide un mensaje largo en fragmentos respetando bloques de código y líneas relacionadas.
        Los bloques de código se mantienen íntegros, incluso si sobrepasan el límite de caracteres.

        :param message: Mensaje completo a dividir.
        :param limit: Límite de caracteres por fragmento.
        :return: Lista de fragmentos de mensaje.
        """
        lines = message.splitlines()
        chunks = []
        current_chunk = ""
        inside_code_block = False
        current_code_block = ""

        for line in lines:
            if line.strip().startswith("```"):
                if inside_code_block:
                    inside_code_block = False
                    current_code_block += line + "\n"
                    if len(current_chunk) + len(current_code_block) > limit:
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                        chunks.append(current_code_block.strip())
                        current_chunk = ""
                    else:
                        current_chunk += current_code_block
                    current_code_block = ""
                else:
                    inside_code_block = True
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = line + "\n"
            elif inside_code_block:
                current_code_block += line + "\n"
            else:
                if len(current_chunk) + len(line) + 1 > limit:
                    chunks.append(current_chunk.strip())
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        if current_code_block.strip():
            chunks.append(current_code_block.strip())

        return chunks

    @staticmethod
    def send_to_telegram(bot_token, chat_id, message):
        """
        Envía mensajes a Telegram en fragmentos, asegurando que cada uno se procese correctamente.

        :param bot_token: Token del bot de Telegram.
        :param chat_id: ID del chat de Telegram.
        :param chunks: Lista de fragmentos del mensaje a enviar.
        """
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }

        try:
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                print(f"Mensaje enviado exitosamente a {chat_id}.")
            else:
                print(f"Error al enviar el mensaje: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar el mensaje: {e}")

    @staticmethod
    def send_to_discord(bot_token, chat_id, chunks):
        """
        Envía mensajes a Discord en fragmentos.
        """
        url = f"https://discord.com/api/v10/channels/{chat_id}/messages"
        headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json",
        }

        for chunk in chunks:
            data = {"content": chunk}
            response = requests.post(
                url, data=json.dumps(data), headers=headers, timeout=10
            )
            if response.status_code == 200:
                print("Mensaje enviado exitosamente.")
            else:
                print(f"Error al enviar mensaje: {response.status_code}, {response.text}")

    def send_message_bot(self, bot_token, chat_id, feature, formatted_message):
        """
        Envía un mensaje a Telegram o Discord dependiendo del formato del token.
        """
        message = self.format_message(feature, formatted_message)
        chunks = self.split_message(message)

        if len(bot_token.split(":")) == 2 and not len(bot_token) == 64:
            self.send_to_telegram(bot_token, chat_id, message)
        else:
            self.send_to_discord(bot_token, chat_id, chunks)
