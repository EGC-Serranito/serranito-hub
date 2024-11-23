import requests
import yaml
import json
import os


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

    def get_bot_token(self, bot_name, bottokens_path="app/modules/botintegration/assets/bottokens.yaml"):
        """
        Obtiene el token de un bot específico a partir del archivo .env y los datos en bottokens.yaml.

        :param bot_name: Nombre del bot (por ejemplo, "@uvlhub-telegram1").
        :param bottokens_path: Ruta al archivo YAML con las configuraciones de los bots.
        :param env_path: Ruta al archivo .env.
        :return: Token del bot como cadena.
        :raises: FileNotFoundError, KeyError o ValueError si ocurre algún problema.
        """
        try:
            # Cargar el archivo bottokens.yaml
            with open(bottokens_path, "r") as file:
                bottokens_data = yaml.safe_load(file)

            # Buscar el bot en la lista de tokens
            bot_entry = next(
                (entry for entry in bottokens_data.get("bottokens", []) if entry["name"] == bot_name),
                None
            )

            if not bot_entry:
                raise ValueError(f"Bot name '{bot_name}' not found in {bottokens_path}.")

            # Extraer la variable del token (por ejemplo, {BOT_TELEGRAM1})
            token_var = bot_entry["token"]

            # Obtener el valor de la variable del token
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
        # Check if the URL already starts with http:// or https://
        if not url.startswith(("http://", "https://")):
            url = "http://" + url  # Add http:// if no scheme present
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
        # Cargar los mensajes desde el archivo YAML
        messages_config = self.load_messages()
        messages = messages_config.get("messages", {})

        # Iterar sobre las características proporcionadas
        for feature in features:
            # Extraer el mensaje desde la configuración usando match-case
            match feature:
                case "AUTH":
                    from app.modules.profile.models import UserProfile
                    from app.modules.auth.models import User
                    message_template = messages.get("AUTH", {}).get("message", "")
                    from app.modules.botintegration.models import TreeNode
                    # Fetch nodes from the tree in the database
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
                    message_template = messages.get("DATASET", {}).get("message", "")
                    from app.modules.botintegration.models import TreeNode
                    # Fetch nodes from the tree in the database
                    tree_node = TreeNode.query.filter(TreeNode.name == chat_id).first()
                    datasets = DataSet.query.join(DSMetaData).filter(
                        DataSet.user_id == tree_node.user_id, DSMetaData.dataset_doi.isnot(None)
                    ).order_by(DataSet.created_at.desc()).all()

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
                                url_view = f"{BASE_URL}/file/view/{file.id}"
                                print(url_view)
                                url_download = (
                                    f"{BASE_URL}/file/download/{file.id}"
                                )

                                # View and download links
                                list_content += f"📥 *Download File*: [{file.name}]({url_download})\n"

                                # Make request to get file content
                                try:
                                    response = requests.get(url_view, timeout=10)
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
                    response = requests.post(f"{BASE_URL}/explore", json={}, timeout=10)
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
                    self.send_messages_flamapy(bot_token, chat_id, BASE_URL)
                    formatted_message = message_template
                case "FAKENODO":
                    response = requests.get(f"{BASE_URL}/fakenodo/api", timeout=10)
                    if response.status_code == 200:
                        # Convertir la respuesta JSON a un diccionario
                        data = response.json()
                        print(data.get("message", "No conection"))
                    user_data = {
                        "connection": data.get("message", "No conection")
                    }
                    message_template = messages.get("FAKENODO", {}).get("message", "")
                    formatted_message = message_template.format(**user_data)
                case "HUBSTATS":
                    response = requests.get(f"{BASE_URL}/hub-stats", timeout=10)
                    if response.status_code == 200:
                        # Convertir la respuesta JSON a un diccionario
                        data = response.json()
                        message_template = messages.get("HUBSTATS", {}).get("message", "")
                        formatted_message = message_template.format(**response.json())
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

    def send_messages_flamapy(self, bot_token, chat_id, BASE_URL):
        """
        Obtiene los mensajes enviados al bot y responde a cada uno de ellos con "Hola, soy el bot".
        """
        if (len(bot_token.split(":")) == 2 and not len(bot_token) == 64):
            url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
            response = requests.get(url)
            webhook_info = response.json()

            if webhook_info["result"]["url"]:
                # Si hay un webhook activo, eliminarlo
                delete_webhook_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
                delete_response = requests.get(delete_webhook_url)
                if delete_response.status_code == 200:
                    print("Webhook eliminado con éxito.")
                else:
                    print(f"Error al eliminar el webhook: {delete_response.text}")
            last_update_id = None
            # Obtener las actualizaciones (mensajes enviados al bot)
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            if last_update_id is not None:
                url += f"?offset={last_update_id + 1}"

            response = requests.get(url, timeout=10)
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
                response = requests.get(url, timeout=10)

                if "message" in update:
                    chat_id_messages = update["message"]["chat"]["id"]  # ID del chat
                    message_id = update["message"][
                        "message_id"
                    ]  # ID del mensaje recibido
                    uvl_message = update["message"].get("text", "Mensaje sin texto")

                    if int(chat_id) == int(chat_id_messages):
                        # Llamar a la API de Flamapy con el mensaje
                        response = requests.post(
                            f"{BASE_URL}/flamapy/check_uvl",
                            json={
                                "text": uvl_message
                            }, timeout=10)

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
                            data=data, timeout=10)
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
            params = {"limit": 10}  # Limita la cantidad de mensajes a obtener

            # Los headers incluyen el token de autorización del bot
            headers = {"Authorization": f"Bot {bot_token}"}

            # Realiza la solicitud GET para obtener los mensajes más recientes
            response = requests.get(url, headers=headers, params=params, timeout=10)

            # Verifica si la solicitud fue exitosa
            if response.status_code == 200:
                messages = response.json()

                # Muestra los mensajes recientes
                for message in messages:
                    if not message['author'].get('bot', False):
                        print(
                            f"Autor: {message['author']['username']} - Contenido: {message['content']}"
                        )

                        # Realiza la solicitud POST a la API externa para verificar el mensaje
                        external_api_url = f"{BASE_URL}/flamapy/check_uvl"
                        response = requests.post(
                            external_api_url,
                            json={
                                "text": message["content"]
                            }, timeout=10)

                        # Obtiene el texto de respuesta de la API externa
                        response_text = response.json().get("error", "Valid Model")

                        # Configuración de los headers para responder al mensaje en Discord
                        headers = {
                            "Authorization": f"Bot {bot_token}",
                            "Content-Type": "application/json",
                        }

                        # Datos para enviar como respuesta al mensaje
                        data = {
                            "content": response_text,
                            "message_reference": {
                                "message_id": message['id']  # Referencia al mensaje original
                            }
                        }

                        # Envia la respuesta al mensaje en Discord
                        send_response = requests.post(
                            url, data=json.dumps(data), headers=headers, timeout=10)

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
                response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)

                # Verificar la respuesta
                if response.status_code == 200:
                    print("Mensaje enviado exitosamente.")
                else:
                    print(
                        f"Error al enviar el mensaje: {response.status_code}, {response.text}"
                    )
