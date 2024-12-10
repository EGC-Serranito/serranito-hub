import pytest
from unittest.mock import MagicMock, patch, Mock
from app.modules.auth.models import User
from app.modules.botintegration.features import FeatureService
from app.modules.botintegration.services import NodeService
from app import create_app


@pytest.fixture
def node_service():
    """Fixture para el servicio NodeService."""
    return NodeService()


@pytest.fixture
def feature_service():
    """Fixture para el servicio NodeService."""
    return FeatureService()


@pytest.fixture
def mock_user():
    app = create_app()
    with app.app_context():
        user = MagicMock(spec=User)
        user.id = 1
        user.temp_folder.return_value = "/mock/temp/folder"
        user.profile.surname = "Doe"
        user.profile.name = "John"
        user.profile.affiliation = "Test University"
        user.profile.orcid = "0000-0001-2345-6789"
        return user


@pytest.fixture
def mock_treenode():
    app = create_app()
    with app.app_context():
        tree_node = MagicMock()
        tree_node.id = 1
        tree_node.name = "0"
        tree_node.user_id = 1
        tree_node.path = "3/@uvlhub_telegram1/4/1959498857/0"
        tree_node.single_child = False
        tree_node.children = [
            MagicMock(
                name="8",
                path="3/@uvlhub_telegram1/4/1959498857/0/8",
                children=[
                    MagicMock(
                        name="AUTH",
                        path="3/@uvlhub_telegram1/4/1959498857/0/8/AUTH",
                        children=[],
                    )
                ],
            )
        ]
        return tree_node


def test_format_message(feature_service):
    """Prueba el formateo de un mensaje para un feature y un mensaje formateado."""
    feature = "test_feature"
    formatted_message = "This is a test message."

    # Llamamos al método estático format_message
    result = feature_service.format_message(feature, formatted_message)

    # Verificamos que el mensaje sea formateado correctamente
    expected_result = (
        f"Message for {feature}:\n{formatted_message}\n\n"
        + "*For more information about this bot, visit:* \n"
        + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)"
    )
    assert result == expected_result


def test_split_message(feature_service):
    """Prueba la división de un mensaje en fragmentos de longitud máxima especificada."""

    # Mensaje de prueba con varias líneas
    message = "This is a test message.\nIt will be split into chunks.\nEach chunk should not exceed the character limit"
    limit = 50  # Límite de caracteres por fragmento

    # Llamamos al método estático split_message
    result = feature_service.split_message(message, limit)

    # Fragmentos esperados basados en el límite de caracteres
    expected_result = [
        "This is a test message.\n",
        "It will be split into chunks.\n",
        "Each chunk should not exceed the character limit\n",
    ]

    # Verificamos que el resultado coincida con el esperado
    assert result == expected_result


def test_split_message_with_large_input(feature_service):
    """Prueba la división de un mensaje muy largo en fragmentos pequeños."""
    message = "A" * 2000
    limit = 1000
    result = feature_service.split_message(message, limit)
    assert len(result) == 2


def test_split_message_without_newlines(feature_service):
    """Prueba la división de un mensaje sin saltos de línea."""

    message = (
        "ThisIsASingleLineMessageThatExceedsTheLimit" * 10
    )
    limit = 50

    result = feature_service.split_message(message, limit)

    assert len(result) == 2


def test_send_to_telegram_success(feature_service):
    """Prueba el envío exitoso de mensajes a Telegram en fragmentos."""
    bot_token = "dummy_bot_token"
    chat_id = "dummy_chat_id"
    chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
    # Simulamos una respuesta exitosa de la API de Telegram (status code 200)
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response

        # Llamamos al método estático send_to_telegram
        feature_service.send_to_telegram(bot_token, chat_id, chunks)

        # Verificamos que requests.post fue llamado 3 veces (por los 3 fragmentos)
        assert mock_post.call_count == 3


def test_send_to_telegram_failure(feature_service):
    """Prueba el fallo al enviar mensajes a Telegram debido a un error en la API."""
    bot_token = "dummy_bot_token"
    chat_id = "dummy_chat_id"
    chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
    # Simulamos una respuesta fallida de la API de Telegram (status code 500)
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        # Llamamos al método estático send_to_telegram
        feature_service.send_to_telegram(bot_token, chat_id, chunks)

        # Verificamos que requests.post fue llamado 3 veces
        assert mock_post.call_count == 3

        # Verificamos que los datos enviados sean correctos


def test_send_to_telegram_empty_chunks(feature_service):
    """Prueba el envío de mensajes cuando no hay fragmentos de mensaje."""

    bot_token = "dummy_bot_token"
    chat_id = "dummy_chat_id"
    chunks = []  # Lista vacía de fragmentos

    # Simulamos una respuesta exitosa de la API de Telegram (status code 200)
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response

        # Llamamos al método estático send_to_telegram
        feature_service.send_to_telegram(bot_token, chat_id, chunks)

        # Verificamos que requests.post no fue llamado ya que no hay fragmentos
        mock_post.assert_not_called()
