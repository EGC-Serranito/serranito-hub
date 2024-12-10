import pytest
from unittest.mock import MagicMock, patch, Mock
from app.modules.auth.models import User
from app.modules.botintegration.features import FeatureService
from app.modules.botintegration.services import NodeService
from app import create_app
import os


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

    result = feature_service.format_message(feature, formatted_message)

    expected_result = (
        f"Message for {feature}:\n{formatted_message}\n\n"
        + "*For more information about this bot, visit:* \n"
        + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)"
    )
    assert result == expected_result


def test_split_message(feature_service):
    """Prueba la división de un mensaje en fragmentos de longitud máxima especificada."""

    message = "This is a test message.\nIt will be split into chunks.\nEach chunk should not exceed the character limit"
    limit = 50

    result = feature_service.split_message(message, limit)

    expected_result = [
        "This is a test message.\n",
        "It will be split into chunks.\n",
        "Each chunk should not exceed the character limit\n",
    ]

    assert result == expected_result


def test_split_message_with_large_input(feature_service):
    """Prueba la división de un mensaje muy largo en fragmentos pequeños."""
    message = "A" * 2000
    limit = 1000
    result = feature_service.split_message(message, limit)
    assert len(result) == 2


def test_split_message_without_newlines(feature_service):
    """Prueba la división de un mensaje sin saltos de línea."""

    message = "ThisIsASingleLineMessageThatExceedsTheLimit" * 10
    limit = 50

    result = feature_service.split_message(message, limit)

    assert len(result) == 2


def test_send_to_telegram_success(feature_service):
    """Prueba el envío exitoso de mensajes a Telegram en fragmentos."""
    chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]

    with patch("os.getenv") as mock_getenv:

        mock_getenv.side_effect = lambda key: {
            "BOT_TOKEN": "dummy_bot_token",
            "CHAT_ID": "dummy_chat_id",
        }.get(key)

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_post.return_value = mock_response

            bot_token = os.getenv("BOT_TOKEN")
            chat_id = os.getenv("CHAT_ID")

            feature_service.send_to_telegram(bot_token, chat_id, chunks)

            assert mock_post.call_count == 3


def test_send_to_telegram_failure(feature_service):
    """Prueba el fallo al enviar mensajes a Telegram debido a un error en la API."""
    chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]

    with patch("os.getenv") as mock_getenv:

        mock_getenv.side_effect = lambda key: {
            "BOT_TOKEN": "dummy_bot_token",
            "CHAT_ID": "dummy_chat_id",
        }.get(key)
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response
            bot_token = os.getenv("BOT_TOKEN")
            chat_id = os.getenv("CHAT_ID")

            feature_service.send_to_telegram(bot_token, chat_id, chunks)

            assert mock_post.call_count == 3


def test_send_to_telegram_empty_chunks(feature_service):
    """Prueba el envío de mensajes cuando no hay fragmentos de mensaje."""
    chunks = []
    with patch("os.getenv") as mock_getenv:

        mock_getenv.side_effect = lambda key: {
            "BOT_TOKEN": "dummy_bot_token",
            "CHAT_ID": "dummy_chat_id",
        }.get(key)
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_post.return_value = mock_response
            bot_token = os.getenv("BOT_TOKEN")
            chat_id = os.getenv("CHAT_ID")
            feature_service.send_to_telegram(bot_token, chat_id, chunks)

            mock_post.assert_not_called()
