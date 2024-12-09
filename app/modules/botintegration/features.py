import requests
import yaml
import json
import os
from datetime import datetime


class FeatureService:
    def load_messages(
        self, file_path="app/modules/botintegration/assets/messages.yaml"
    ):
        """
        Carga el archivo YAML con la configuración de mensajes.

        :param file_path: Ruta del archivo YAML (opcional).
        :return: Datos cargados del archivo YAML.
        """
        try:
            with open(file_path, "r") as file:
                data = yaml.safe_load(file)
            return data
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            raise
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            raise

    def get_bot_token(
        self,
        bot_name,
        bottokens_path="app/modules/botintegration/assets/bottokens.yaml",
    ):
        """
        Obtiene el token de un bot específico a partir del archivo .env y los datos en bottokens.yaml.

        :param bot_name: Nombre del bot (por ejemplo, "@uvlhub-telegram1").
        :param bottokens_path: Ruta al archivo YAML con las configuraciones de los bots.
        :param env_path: Ruta al archivo .env.
        :return: Token del bot como cadena.
        :raises: FileNotFoundError, KeyError o ValueError si ocurre algún problema.
        """
        try:
            with open(bottokens_path, "r") as file:
                bottokens_data = yaml.safe_load(file)

            bot_entry = next(
                (
                    entry
                    for entry in bottokens_data.get("bottokens", [])
                    if entry["name"] == bot_name
                ),
                None,
            )

            if not bot_entry:
                raise ValueError(
                    f"Bot name '{bot_name}' not found in {bottokens_path}."
                )

            token_var = bot_entry["token"]

            bot_token = os.getenv(token_var)

            if not bot_token:
                raise ValueError(f"Token variable '{token_var}' not found or empty.")

            return bot_token

        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def transform_to_full_url(self, url):
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        return url

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
                    from app.modules.hubfile.models import HubfileViewRecord
                    from app import db
                    from flask import current_app, jsonify, make_response, request
                    from flask_login import current_user
                    import uuid
                    message_template = messages.get("DATASET", {}).get("message", "")
                    from app.modules.botintegration.models import TreeNode

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
                        publication_type = d.ds_meta_data.publication_type.name.replace(
                            "_", " "
                        ).title()
                        doi = d.get_uvlhub_doi()

                        list_content += f"🔹 *Title*: {title}\n"
                        list_content += f"📄 *Description*: {description}\n"
                        list_content += f"📚 *Publication Type*: {publication_type}\n"
                        list_content += f"🌐 *DOI*: [{doi}]({doi})\n"

                        for feature_model in d.feature_models:
                            for file in feature_model.files:
                                list_content += f"\n🔸 *File*: {file.name}\n"

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

                                        user_cookie = request.cookies.get("view_cookie")
                                        if not user_cookie:
                                            user_cookie = str(uuid.uuid4())

                                        existing_record = HubfileViewRecord.query.filter_by(
                                            user_id=current_user.id if current_user.is_authenticated else None,
                                            file_id=file.id,
                                            view_cookie=user_cookie,
                                        ).first()

                                        if not existing_record:
                                            new_view_record = HubfileViewRecord(
                                                user_id=current_user.id if current_user.is_authenticated else None,
                                                file_id=file.id,
                                                view_date=datetime.now(),
                                                view_cookie=user_cookie,
                                            )
                                            db.session.add(new_view_record)
                                            db.session.commit()

                                        response = jsonify({"success": True, "content": content})
                                        if not request.cookies.get("view_cookie"):
                                            response = make_response(response)
                                            response.set_cookie("view_cookie",
                                                                user_cookie, max_age=60 * 60 * 24 * 365 * 2)

                                        if response.status_code == 200:
                                            data = response.get_json()
                                            file_content = data.get("content", "")
                                            if file_content:
                                                list_content += "\n*👨‍💻 File Content (UVL)*:\n"
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
                                list_content += f"📥 *Download File*: {url_download}\n"

                        user_data = {"datasets": list_content}
                        formatted_message = message_template.format(**user_data)
                case "EXPLORE":
                    from app.modules.explore.services import ExploreService
                    criteria = {}
                    datasets = ExploreService().filter(**criteria)
                    datasets_info = []
                    for data in datasets:
                        dataset = data.to_dict()
                        dataset_info = (
                            f"📂 *{dataset['title']}*\n"
                            f"📝 _{dataset['description']}_\n"
                            f"👨‍💻 *Authors*: {', '.join([author['name'] for author in dataset['authors']])}\n"
                            f"🏷 *Tags*: {', '.join(dataset['tags'])}\n"
                            f"📦 *Size*: {dataset['total_size_in_human_format']}\n"
                            f"🌐 [DOI]({dataset['url']}) | [Download]({dataset['download']})\n"
                            "-------------------------"
                        )
                        datasets_info.append(dataset_info)

                        formatted_datasets = "\n\n".join(datasets_info)

                        formatted_message = f"✨ *Explore the datasets below* ✨\n\n{formatted_datasets}"
                case "FLAMAPY":
                    message_template = messages.get("FLAMAPY", {}).get("message", "")
                    self.send_messages_flamapy(bot_token, chat_id, BASE_URL)
                    formatted_message = message_template
                case "FAKENODO":
                    data = {"status": "success", "message": "Connected to Fakenodo API"}
                    user_data = {"connection": data.get("message", "No conection")}
                    message_template = messages.get("FAKENODO", {}).get("message", "")
                    formatted_message = message_template.format(**user_data)
                case "HUBSTATS":

                    from app.modules.dataset.services import DataSetService
                    from app.modules.featuremodel.services import FeatureModelService
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.info("Access index")
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

    def send_messages_flamapy(self, bot_token, chat_id, BASE_URL):
        """
        Obtiene los mensajes enviados al bot y responde a cada uno de ellos con "Hola, soy el bot".
        """
        from flamapy.metamodels.fm_metamodel.transformations import (
            UVLReader
        )
        import tempfile
        from antlr4.error.ErrorListener import ErrorListener
        if len(bot_token.split(":")) == 2 and not len(bot_token) == 64:
            url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
            response = requests.get(url, timeout=10)
            webhook_info = response.json()

            if webhook_info["result"]["url"]:
                delete_webhook_url = (
                    f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
                )
                delete_response = requests.get(delete_webhook_url, timeout=10)
                if delete_response.status_code == 200:
                    print("Webhook eliminado con éxito.")
                else:
                    print(f"Error al eliminar el webhook: {delete_response.text}")
            last_update_id = None
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            if last_update_id is not None:
                url += f"?offset={last_update_id + 1}"

            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"Error al obtener actualizaciones: {response.text}")
                return

            updates = response.json()

            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
                if last_update_id is not None:
                    url += f"?offset={last_update_id + 1}"
                response = requests.get(url, timeout=10)

                if "message" in update:
                    chat_id_messages = update["message"]["chat"]["id"]
                    message_id = update["message"]["message_id"]
                    uvl_message = update["message"].get("text", "Mensaje sin texto")

                    if int(chat_id) == int(chat_id_messages):
                        class CustomErrorListener(ErrorListener):
                            def __init__(self):
                                self.errors = []

                            def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
                                self.errors.append(f"Line {line}:{column} - {msg}")

                        try:
                            uvl_text = uvl_message

                            with tempfile.NamedTemporaryFile(delete=False, suffix=".uvl") as temp_file:
                                temp_file.write(uvl_text.encode("utf-8"))
                                temp_path = temp_file.name

                            try:
                                UVLReader(temp_path).transform()
                                response_text = "Valid Model"
                            except Exception as e:
                                response_text = f"Error in the validation of the model: {str(e)}"

                        except Exception as e:
                            response_text = f"General error: {str(e)}"

                        data = {
                            "chat_id": chat_id,
                            "text": response_text,
                            "reply_to_message_id": message_id,
                        }

                        send_response = requests.post(
                            f"https://api.telegram.org/bot{bot_token}/sendMessage",
                            data=data,
                            timeout=10,
                        )

                        if send_response.status_code == 200:
                            print(f"Respondido al mensaje {message_id} en el chat {chat_id}")
                        else:
                            print(f"Error al responder al mensaje {message_id}: {send_response.text}")

        else:
            url = f"https://discord.com/api/v10/channels/{chat_id}/messages"

            params = {"limit": 10}

            headers = {"Authorization": f"Bot {bot_token}"}

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                messages = response.json()

                for message in messages:
                    if not message["author"].get("bot", False):
                        print(
                            f"Autor: {message['author']['username']} - Contenido: {message['content']}"
                        )

                        class CustomErrorListener(ErrorListener):
                            def __init__(self):
                                self.errors = []

                            def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
                                self.errors.append(f"Line {line}:{column} - {msg}")

                        try:
                            uvl_text = message["content"]

                            with tempfile.NamedTemporaryFile(delete=False, suffix=".uvl") as temp_file:
                                temp_file.write(uvl_text.encode("utf-8"))
                                temp_path = temp_file.name

                            try:
                                UVLReader(temp_path).transform()
                                response_text = "Valid Model"
                            except Exception as e:
                                response_text = f"Error in the validation of the model: {str(e)}"
                        except Exception as e:
                            response_text = f"General error: {str(e)}"

                        headers = {
                            "Authorization": f"Bot {bot_token}",
                            "Content-Type": "application/json",
                        }

                        data = {
                            "content": response_text,
                            "message_reference": {"message_id": message["id"]},
                        }

                        send_response = requests.post(
                            url, data=json.dumps(data), headers=headers, timeout=10
                        )

                        if send_response.status_code == 200:
                            print(
                                f"Respondido al mensaje {message['id']} en el chat {chat_id}"
                            )
                        else:
                            print(
                                f"Error al responder al mensaje {message['id']}: {send_response.text}"
                            )
            else:
                print(f"Error al obtener los mensajes: {response.status_code}")

    def send_message_bot(self, bot_token, chat_id, feature, formatted_message):
        """
        Envía un mensaje formateado a un bot de Telegram.
        :param bot_token: Token del bot de Telegram.
        :param chat_id: ID del chat de Telegram al que enviar el mensaje.
        :param feature: La característica para la que se está enviando el mensaje.
        :param formatted_message: Mensaje ya formateado con los datos correspondientes.
        """

        message = (
            f"Message for {feature}:\n{formatted_message}\n\n"
            + "*Para más información sobre este bot, visita:* \n"
            + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)"
        )

        def split_message(message, limit=2000):
            """
            Divide un mensaje largo en fragmentos de menos de `limit` caracteres.
            """
            lines = message.splitlines()
            chunks = []
            current_chunk = ""

            for line in lines:
                if len(current_chunk) + len(line) + 1 > limit:
                    chunks.append(current_chunk)
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"

            if current_chunk:
                chunks.append(current_chunk)

            return chunks

        if len(bot_token.split(":")) == 2 and not len(bot_token) == 64:

            chunks = split_message(message)
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            for chunk in chunks:
                payload = {
                    "chat_id": chat_id,
                    "text": chunk,
                    "parse_mode": "Markdown",
                }

                response = requests.post(url, data=payload, timeout=10)

                if response.status_code == 200:
                    print(f"Mensaje enviado a {chat_id} exitosamente para {feature}.")
                else:
                    print(
                        f"Error al enviar mensaje para {feature}: {response.status_code}"
                    )
        else:
            chunks = split_message(message)
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
                    print(
                        f"Error al enviar el mensaje: {response.status_code}, {response.text}"
                    )
