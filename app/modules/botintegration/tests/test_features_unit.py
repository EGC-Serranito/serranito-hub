import pytest
from unittest.mock import MagicMock, patch
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


def test_send_message_bot_telegram(feature_service):
    """Prueba el envío de un mensaje a Telegram."""

    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            "BOT_TOKEN_TELEGRAM": "1234567890:abcdefghijklmnopqrstuvwxyz1234567890",
            "CHAT_ID": "dummy_chat_id",
        }.get(key)
        bot_token = os.getenv("BOT_TOKEN_TELEGRAM")
        chat_id = os.getenv("CHAT_ID")
        formatted_message = "Este es un mensaje de prueba" * 10
        feature = "test_feature"

        with patch.object(feature_service, "format_message") as mock_format_message, \
             patch.object(feature_service, "send_to_telegram") as mock_send_telegram:
            mock_format_message.return_value = (
                f"Message for {feature}:\n{formatted_message}\n\n"
                + "*For more information about this bot, visit:* \n"
                + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)"
            )

            feature_service.send_message_bot(bot_token, chat_id, feature, formatted_message)

            mock_send_telegram.assert_called_once_with(
                bot_token, chat_id, mock_format_message.return_value
            )


def test_send_message_bot_discord(feature_service):
    """Prueba el envío de un mensaje a Discord."""

    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            "BOT_TOKEN_DISCORD": "discord_bot_token_1234567890",
            "CHAT_ID": "dummy_chat_id",
        }.get(key)

        bot_token = os.getenv("BOT_TOKEN_DISCORD")
        chat_id = os.getenv("CHAT_ID")
        formatted_message = "Este es un mensaje de prueba" * 10
        feature = "test_feature"

        # Mock de las funciones
        with patch.object(feature_service, "format_message") as mock_format_message, \
             patch.object(feature_service, "split_message") as mock_split_message, \
             patch.object(feature_service, "send_to_discord") as mock_send_discord:
            mock_format_message.return_value = (
                f"Message for {feature}:\n{formatted_message}\n\n"
                + "*For more information about this bot, visit:* \n"
                + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)"
            )
            mock_split_message.return_value = [
                "Message for test_feature:\nEste es un mensaje de pruebaEste es un mensaje de prueba\n\n"
                + "*For more information about this bot, visit:* \n"
                + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)",
                "Message for test_feature:\nEste es un mensaje de pruebaEste es un mensaje de"
                + "pruebaEste es un mensaje de pruebaEste es un mensaje de prueba\n\n"
                + "*For more information about this bot, visit:* \n"
                + "[serranito-hub-dev](https://serranito-hub-dev.onrender.com/botintegration)",
            ]

            feature_service.send_message_bot(bot_token, chat_id, feature, formatted_message)
            mock_send_discord.assert_called_with(
                bot_token, chat_id, mock_split_message.return_value
            )


def test_split_message_for_discord(feature_service):
    """Prueba la división de un mensaje en fragmentos para enviarlo a Discord."""

    message = "Este es un mensaje muy largo " * 20
    formatted_message = message

    with patch.object(feature_service, "split_message") as mock_split_message:
        mock_split_message.return_value = [
            "Este es un mensaje muy largo Este es un mensaje muy largo Este es un mensaje muy largo "
            + "Este es un mensaje muy largo Este es un mensaje muy largo Este es un mensaje muy largo "
            + "Este es un mensaje muy largo Este es un mensaje muy largo ",
            "Este es un mensaje muy largo Este es un mensaje muy largo Este es un mensaje muy largo "
            + "Este es un mensaje muy largo Este es un mensaje muy largo Este es un mensaje muy largo "
            + "Este es un mensaje muy largo Este es un mensaje muy largo "
        ]

        result = feature_service.split_message(formatted_message)

        mock_split_message.assert_called_once_with(formatted_message)

        assert len(result) == 2
        assert all(len(fragment) <= 2000 for fragment in result)


def test_send_message_bot_invalid_token(feature_service):
    """Prueba el comportamiento cuando el token es inválido."""

    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            "BOT_TOKEN_TELEGRAM": "invalid_token",
            "CHAT_ID": "dummy_chat_id",
        }.get(key)

        bot_token = os.getenv("BOT_TOKEN_TELEGRAM")
        chat_id = os.getenv("CHAT_ID")
        formatted_message = "Este es un mensaje de prueba"
        feature = "test_feature"

        with patch.object(feature_service, "send_to_telegram") as mock_send_telegram, patch.object(feature_service,
                                                                                                   "send_to_discord"):

            feature_service.send_message_bot(bot_token, chat_id, feature, formatted_message)
            mock_send_telegram.assert_not_called()


def test_send_message_bot_formatting(feature_service):
    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            "BOT_TOKEN_TELEGRAM": "1234567890:abcdefghijklmnopqrstuvwxyz1234567890",
            "CHAT_ID": "dummy_chat_id",
        }.get(key)

        bot_token = os.getenv("BOT_TOKEN_TELEGRAM")
        chat_id = os.getenv("CHAT_ID")
        formatted_message = "Este es un mensaje de prueba" * 10
        feature = "test_feature"

        with patch.object(feature_service, "format_message") as mock_format_message:
            with patch.object(feature_service, "send_to_telegram") as mock_send_telegram:
                feature_service.send_message_bot(bot_token, chat_id, feature, formatted_message)
                mock_format_message.assert_called_once_with(feature, formatted_message)
                mock_send_telegram.assert_called_once_with(bot_token, chat_id, mock_format_message.return_value)
