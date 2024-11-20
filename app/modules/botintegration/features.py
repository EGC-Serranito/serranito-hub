import requests
import yaml
from app.modules.profile.models import UserProfile
from app.modules.auth.models import User
from flask_login import current_user
from app.modules.dataset.services import DataSetService
from flask import request
import json

dataset_service = DataSetService()


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
            print("YAML Loaded Successfully:", data)  # Verificar contenido cargado
            return data
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            raise
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            raise

    def send_features_bot(self, bot_token, chat_id, features):
        """
        :param bot_token: Token del bot de Telegram.
        :param chat_id: ID del chat de Telegram al que enviar los mensajes.
        :param features: Lista de características para las cuales enviar mensajes.
        :param user_data: Diccionario con los datos del usuario necesarios para formatear los mensajes.
        """
        # Cargar los mensajes desde el archivo YAML
        messages_config = self.load_messages()
        messages = messages_config.get("messages", {})

        # Iterar sobre las características proporcionadas
        for feature in features:
            # Extraer el mensaje desde la configuración usando match-case
            match feature:
                case "AUTH":
                    message_template = messages.get("AUTH", {}).get("message", "")
                    user = User.query.get(current_user.id)
                    user_profile = UserProfile.query.filter_by(
                        user_id=current_user.id
                    ).first()
                    user_data = {
                        "email": user.email,
                        "name": user_profile.name,
                        "surname": user_profile.surname,
                        "orcid": user_profile.orcid,
                    }
                    formatted_message = message_template.format(**user_data)
                case "DATASET":
                    message_template = messages.get("DATASET", {}).get("message", "")
                    datasets = dataset_service.get_synchronized(current_user.id)
                    list_content = ""

                    for d in datasets:
                        title = d.ds_meta_data.title
                        description = d.ds_meta_data.description
                        publication_type = d.ds_meta_data.publication_type.name.replace(
                            "_", " "
                        ).title()
                        doi = d.get_uvlhub_doi()

                        # Add the title and description prominently
                        list_content += f"🔹 *Title*: {title}\n"
                        list_content += f"📄 *Description*: {description}\n"
                        list_content += f"📚 *Publication Type*: {publication_type}\n"
                        list_content += f"🌐 *DOI*: [{doi}]({doi})\n"

                        # Iterate over feature models and associated files
                        for feature_model in d.feature_models:
                            for file in feature_model.files:
                                # Detail the file associated with each feature model
                                list_content += f"\n🔸 *File*: {file.name}\n"
                                url_view = f"{request.host_url}file/view/{file.id}"
                                print(url_view)
                                url_download = (
                                    f"{request.host_url}file/download/{file.id}"
                                )

                                # View and download links
                                list_content += f"📥 *Download File*: [{file.name}]({url_download})\n"

                                # Make request to get file content
                                try:
                                    response = requests.get(url_view)
                                    if response.status_code == 200:
                                        # Convert the JSON response to a dictionary
                                        data = response.json()
                                        file_content = data.get("content", "")
                                        if file_content:
                                            # Show the content with a title for the code block
                                            list_content += (
                                                "\n*👨‍💻 File Content (UVL)*:\n"
                                            )
                                            list_content += f"\n```uvl\n{file_content[:500]}\n```\n"
                                        else:
                                            list_content += (
                                                "\n*Content not available.*\n"
                                            )
                                    else:
                                        list_content += f"\n(Response code: {response.status_code})\n"
                                except Exception as e:
                                    list_content += f"\n⚠️ *Error occurred while fetching the file content:* {str(e)}\n"

                        list_content += "\n"  # Space between datasets

                    # Crear el cuerpo del mensaje con las listas en formato Markdown
                    user_data = {
                        "datasets": list_content  # El contenido generado se pasa como parte de los datos del usuario
                    }

                    # Crear el mensaje formateado
                    formatted_message = message_template.format(**user_data)
                case "EXPLORE":
                    response = requests.post(f"{request.host_url}explore", json={})
                    if response.status_code == 200:
                        # Convertir la respuesta JSON a un diccionario
                        data = response.json()
                        print(data)  # Verificar los datos obtenidos

                        # Crear una lista con la información de los datasets formateada para Telegram
                        datasets_info = []
                        for dataset in data:
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

                        # Unir toda la información en un solo string
                        formatted_datasets = "\n\n".join(datasets_info)

                        # Crear el mensaje para Telegram
                        formatted_message = f"✨ *Explore the datasets below* ✨\n\n{formatted_datasets}"

                        # Imprimir el mensaje formateado
                        print(formatted_message)
                    else:
                        print(
                            f"Failed to fetch data. Status code: {response.status_code}"
                        )
                case "FLAMAPY":
                    message_template = messages.get("FLAMAPY", {}).get("message", "")
                    self.send_messages_flamapy(bot_token, chat_id)
                    formatted_message = message_template
                case "HUBFILE":
                    message_template = messages.get("HUBFILE", {}).get("message", "")
                    user_data = {
                        "available_models": "Model A, Model B",
                        "last_model_used": "Model C",
                    }
                    formatted_message = message_template.format(**user_data)
                case "FEATURE_MODEL":
                    message_template = messages.get("FEATURE_MODEL", {}).get(
                        "message", ""
                    )
                    formatted_message = message_template.format(**user_data)
                case "FAKENODO":
                    message_template = messages.get("FAKENODO", {}).get("message", "")
                    formatted_message = message_template.format(**user_data)
                case "HUB_STATS":
                    message_template = messages.get("HUB_STATS", {}).get("message", "")
                    formatted_message = message_template.format(**user_data)
                case _:
                    print(
                        f"Feature {feature} no encontrada en la configuración de mensajes."
                    )
                    continue  # Salta al siguiente feature si no es válido

            try:
                # Enviar el mensaje al bot de Telegram
                self.send_message_bot(bot_token, chat_id, feature, formatted_message)
            except KeyError as e:
                print(
                    f"Error formateando el mensaje para la característica {feature}: Faltan datos {e}"
                )

    def send_messages_flamapy(self, bot_token, chat_id):
        """
        Obtiene los mensajes enviados al bot y responde a cada uno de ellos con "Hola, soy el bot".
        """
        if (len(bot_token.split(":")) == 2 and not len(bot_token) == 64):
            last_update_id = None
            # Obtener las actualizaciones (mensajes enviados al bot)
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            if last_update_id is not None:
                url += f"?offset={last_update_id + 1}"

            response = requests.get(url)
            if response.status_code != 200:
                print(f"Error al obtener actualizaciones: {response.text}")
                return

            updates = response.json()

            # Verificar si hay mensajes en las actualizaciones
            for update in updates.get("result", []):
                # Actualizar el último update_id procesado
                last_update_id = update["update_id"]
                url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
                if last_update_id is not None:
                    url += f"?offset={last_update_id + 1}"
                response = requests.get(url)

                if "message" in update:
                    chat_id_messages = update["message"]["chat"]["id"]  # ID del chat
                    message_id = update["message"][
                        "message_id"
                    ]  # ID del mensaje recibido
                    uvl_message = update["message"].get("text", "Mensaje sin texto")

                    if chat_id == chat_id_messages:
                        # Llamar a la API de Flamapy con el mensaje
                        response = requests.post(
                            f"{request.host_url}flamapy/check_uvl",
                            json={
                                "text": uvl_message
                            },  # Corregido: JSON debe ser un diccionario.
                        )

                        # Obtener el texto de respuesta de la API de Flamapy
                        if response.status_code == 200:
                            response_text = response.json().get(
                                "message", "Modelo válido"
                            )
                        else:
                            response_text = response.json().get(
                                "error", "Error al validar el modelo"
                            )

                        data = {
                            "chat_id": chat_id,
                            "text": response_text,
                            "reply_to_message_id": message_id,
                        }

                        # Enviar la respuesta
                        send_response = requests.post(
                            f"https://api.telegram.org/bot{bot_token}/sendMessage",
                            data=data,
                        )
                        if send_response.status_code == 200:
                            print(
                                f"Respondido al mensaje {message_id} en el chat {chat_id}"
                            )
                        else:
                            print(
                                f"Error al responder al mensaje {message_id}: {send_response.text}"
                            )
        else:
            # La URL del endpoint para obtener mensajes de un canal específico
            url = f"https://discord.com/api/v10/channels/{chat_id}/messages"

            # Parámetros para obtener solo el mensaje más reciente
            params = {"limit": 1}  # Limita la cantidad de mensajes a obtener

            # Los headers incluyen el token de autorización del bot
            headers = {"Authorization": f"Bot {bot_token}"}

            # Realiza la solicitud GET para obtener los mensajes más recientes
            response = requests.get(url, headers=headers, params=params)

            # Verifica si la solicitud fue exitosa
            if response.status_code == 200:
                messages = response.json()

                # Muestra los mensajes recientes
                for message in messages:
                    print(
                        f"Autor: {message['author']['username']} - Contenido: {message['content']}"
                    )

                    # Realiza la solicitud POST a la API externa para verificar el mensaje
                    external_api_url = f"{request.host_url}flamapy/check_uvl"
                    response = requests.post(
                        external_api_url,
                        json={
                            "text": message["content"]
                        },  # Corregido: JSON debe ser un diccionario
                    )

                    # Obtiene el texto de respuesta de la API externa
                    response_text = response.json().get("error", "Valid Model")

                    # Configuración de los headers para responder al mensaje en Discord
                    headers = {
                        "Authorization": f"Bot {bot_token}",
                        "Content-Type": "application/json",
                    }

                    # Datos para enviar como respuesta al mensaje
                    data = {"content": response_text}

                    # Envia la respuesta al mensaje en Discord
                    send_response = requests.post(
                        url, data=json.dumps(data), headers=headers
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
            f"Message for {feature}:\n{formatted_message}\n\n"  # Título en negrita
            + "*Para más información sobre este bot, visita:* \n"
            + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)"
        )

        # Función para dividir el mensaje en fragmentos de menos de 2000 caracteres
        def split_message(message, limit=2000):
            """
            Divide un mensaje largo en fragmentos de menos de `limit` caracteres.
            """
            lines = message.splitlines()  # Dividir el mensaje en líneas
            chunks = []
            current_chunk = ""

            for line in lines:
                # Si añadir esta línea excede el límite, guardar el chunk actual y empezar uno nuevo
                if len(current_chunk) + len(line) + 1 > limit:
                    chunks.append(current_chunk)
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"

            if current_chunk:  # Añadir el último chunk si no está vacío
                chunks.append(current_chunk)

            return chunks

        if (len(bot_token.split(":")) == 2 and not len(bot_token) == 64):
            # Crear el mensaje con estilo Markdown

            chunks = split_message(message)

            # URL de la API de Telegram para enviar el mensaje
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            for chunk in chunks:
                # Datos a enviar en la solicitud POST (con formato Markdown habilitado)
                payload = {
                    "chat_id": chat_id,
                    "text": chunk,
                    "parse_mode": "Markdown",
                }

                # Realizar la solicitud POST a la API de Telegram
                response = requests.post(url, data=payload, timeout=10)

                # Comprobar si la solicitud fue exitosa
                if response.status_code == 200:
                    print(f"Mensaje enviado a {chat_id} exitosamente para {feature}.")
                else:
                    print(
                        f"Error al enviar mensaje para {feature}: {response.status_code}"
                    )
        else:
            # Dividir el mensaje en fragmentos
            chunks = split_message(message)
            url = f"https://discord.com/api/v10/channels/{chat_id}/messages"
            # Configuración de los headers
            headers = {
                "Authorization": f"Bot {bot_token}",
                "Content-Type": "application/json",
            }

            # Enviar cada fragmento
            for chunk in chunks:
                data = {"content": chunk}
                response = requests.post(url, data=json.dumps(data), headers=headers)

                # Verificar la respuesta
                if response.status_code == 200:
                    print("Mensaje enviado exitosamente.")
                else:
                    print(
                        f"Error al enviar el mensaje: {response.status_code}, {response.text}"
                    )
