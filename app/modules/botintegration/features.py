import requests
import yaml
from app.modules.profile.models import UserProfile
from app.modules.auth.models import User
from flask_login import current_user
from app.modules.dataset.services import DataSetService
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from flask import url_for, request
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
        Envía mensajes formateados a un bot de Telegram para las características solicitadas usando mensajes cargados dinámicamente.

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
                    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
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
                        publication_type = d.ds_meta_data.publication_type.name.replace('_', ' ').title()
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
                                url_view = f'{request.host_url}file/view/{file.id}'
                                url_download = f'{request.host_url}file/download/{file.id}'
                                
                                # View and download links
                                list_content += f"📥 *Download File*: [{file.name}]({url_download})\n"
                                
                                # Make request to get file content
                                try:
                                    response = requests.get(url_view)
                                    if response.status_code == 200:
                                        # Convert the JSON response to a dictionary
                                        data = response.json()
                                        file_content = data.get('content', '')
                                        if file_content:
                                            # Show the content with a title for the code block
                                            list_content += "\n*👨‍💻 File Content (UVL)*:\n"
                                            list_content += f"\n```uvl\n{file_content[:500]}\n```\n"  # Show only the first 500 characters
                                        else:
                                            list_content += "\n*Content not available.*\n"
                                    else:
                                        list_content += f"\n⚠️ *Error retrieving the file.* (Response code: {response.status_code})\n"
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
                    message_template = messages.get("EXPLORE", {}).get("message", "")
                    user_data = {
                        "explore_areas": "sales, marketing"
                    }
                    formatted_message = message_template.format(**user_data)
                case "FLAMAPY":
                    message_template = messages.get("FLAMAPY", {}).get("message", "")
                    user_data = {
                        "analysis_types": "clustering, regression",
                        "top_features": "Feature A, Feature B",
                        "available_models": "Model A, Model B",
                        "last_model_used": "Model C"
                    }
                    formatted_message = message_template.format(**user_data)
                case "HUBFILE":
                    message_template = messages.get("HUBFILE", {}).get("message", "")
                    user_data = {
                        "available_models": "Model A, Model B",
                        "last_model_used": "Model C"
                    }
                    formatted_message = message_template.format(**user_data)
                case "FEATURE_MODEL":
                    message_template = messages.get("FEATURE_MODEL", {}).get("message", "")
                    formatted_message = message_template.format(**user_data)
                case "FAKENODO":
                    message_template = messages.get("FAKENODO", {}).get("message", "")
                    formatted_message = message_template.format(**user_data)
                case "HUB_STATS":
                    message_template = messages.get("HUB_STATS", {}).get("message", "")
                    formatted_message = message_template.format(**user_data)
                case _:
                    print(f"Feature {feature} no encontrada en la configuración de mensajes.")
                    continue  # Salta al siguiente feature si no es válido

            if not message_template:
                print(f"No se encontró un mensaje válido para la característica {feature}.")
                continue

            try:
                # Enviar el mensaje al bot de Telegram
                self.send_message_bot(bot_token, chat_id, feature, formatted_message)
            except KeyError as e:
                print(
                    f"Error formateando el mensaje para la característica {feature}: Faltan datos {e}"
                )

    def sendPhotoImages(self, bot_token, chat_id, datasets):
        """
        Genera una tabla profesional en formato Markdown, la renderiza como imagen y la envía por Telegram.
        """
        table_content = ""

        for d in datasets:
            title = d.ds_meta_data.title
            description = d.ds_meta_data.description
            publication_type = d.ds_meta_data.publication_type.name.replace('_', ' ').title()
            doi = d.get_uvlhub_doi()
            table_content += f"| {title} | {description} | {publication_type} | [DOI]({doi}) |\n"

        # 2. Crear la imagen con Pillow
        img_width = 950
        cell_height = 40
        cell_widths = [200, 300, 150, 300]  # Definir un ancho fijo para cada columna (ajustar según sea necesario)
        
        # Estimar la altura de la imagen según el número de datasets
        img_height = 100 + len(datasets) * cell_height
        img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 3. Definir una fuente y colores
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except IOError:
            font = ImageFont.load_default()

        header_color = (200, 200, 200)  # Color de fondo para el encabezado
        row_colors = [(255, 255, 255), (240, 240, 240)]  # Colores alternos para filas
        text_color = (0, 0, 0)
        border_color = (0, 0, 0)

        # 4. Dibujar la tabla
        y_offset = 10
        x_offset = 20

        # Dibujar el encabezado
        columns = ["Title", "Description", "Publication Type", "DOI"]
        for i, col in enumerate(columns):
            x_start = x_offset + sum(cell_widths[:i])  # Sumar los anchos de las columnas anteriores
            x_end = x_start + cell_widths[i]
            draw.rectangle([x_start, y_offset, x_end, y_offset + cell_height], fill=header_color, outline=border_color)
            draw.text((x_start + 10, y_offset + 10), col, font=font, fill=text_color)
        
        y_offset += cell_height

        # Dibujar las filas de los datasets
        for idx, d in enumerate(datasets):
            row_color = row_colors[idx % 2]  # Alternar colores de fila
            row_data = [
                d.ds_meta_data.title,
                d.ds_meta_data.description,
                d.ds_meta_data.publication_type.name.replace('_', ' ').title(),
                d.get_uvlhub_doi()
            ]
            
            for j, cell in enumerate(row_data):
                x_start = x_offset + sum(cell_widths[:j])  # Sumar los anchos de las columnas anteriores
                x_end = x_start + cell_widths[j]
                draw.rectangle([x_start, y_offset, x_end, y_offset + cell_height], fill=row_color, outline=border_color)
                cell_text = str(cell) # Enlace DOI
                draw.text((x_start + 10, y_offset + 10), cell_text, font=font, fill=text_color)

            y_offset += cell_height

        # 5. Guardar la imagen en un buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # 6. Enviar la imagen a Telegram
        url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
        files = {'photo': buffer}
        params = {'chat_id': chat_id}

        response = requests.post(url, data=params, files=files)

        # 7. Manejar la respuesta de Telegram
        if response.status_code == 200:
            print("Imagen de la tabla enviada con éxito.")
        else:
            print(f"Error al enviar la imagen: {response.status_code} - {response.text}")


    def send_message_bot(self, bot_token, chat_id, feature, formatted_message):
        """
        Envía un mensaje formateado a un bot de Telegram.

        :param bot_token: Token del bot de Telegram.
        :param chat_id: ID del chat de Telegram al que enviar el mensaje.
        :param feature: La característica para la que se está enviando el mensaje.
        :param formatted_message: Mensaje ya formateado con los datos correspondientes.
        """
        # Crear el mensaje con estilo Markdown
        message = (
            f"Message for {feature}:\n{formatted_message}\n\n"  # Título en negrita
            + "*Para más información sobre este bot, visita:* \n"
            + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)"
        )

        # URL de la API de Telegram para enviar el mensaje
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        # Datos a enviar en la solicitud POST (con formato Markdown habilitado)
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }

        # Realizar la solicitud POST a la API de Telegram
        response = requests.post(url, data=payload, timeout=10)

        # Comprobar si la solicitud fue exitosa
        if response.status_code == 200:
            print(f"Mensaje enviado a {chat_id} exitosamente para {feature}.")
        else:
            print(f"Error al enviar mensaje para {feature}: {response.status_code}")
    
    