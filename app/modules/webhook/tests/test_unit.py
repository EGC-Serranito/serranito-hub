import pytest
from unittest.mock import patch, MagicMock, call
from app.modules.webhook.services import WebhookService
from werkzeug.exceptions import InternalServerError
from flask import abort
import docker
import subprocess


@pytest.fixture
def webhook_service():
    return WebhookService()


@pytest.fixture
def mock_container():
    container = MagicMock()
    container.id = "mock_container_id"
    container.attrs = {
        'Mounts': [
            {'Name': 'mock_volume', 'Destination': '/app'}
        ]
    }
    return container


def test_get_web_container_found(webhook_service, mock_container):
    with patch("app.modules.webhook.services.client") as mock_client:
        mock_client.containers.get.return_value = mock_container
        container = webhook_service.get_web_container()
        assert container == mock_container


def test_get_web_container_not_found(webhook_service):
    # Parchea 'client' y 'abort' en el contexto de 'app.modules.webhook.services'
    with patch("app.modules.webhook.services.client") as mock_client, patch("app.modules.webhook.services.abort") as mock_abort:
        mock_client.containers.get.side_effect = docker.errors.NotFound("Container not found")
        webhook_service.get_web_container()
        mock_abort.assert_called_once_with(404, description="Web container not found.")


def test_get_volume_name(webhook_service, mock_container):
    volume_name = webhook_service.get_volume_name(mock_container)
    assert volume_name == 'mock_volume'


def test_get_volume_name_no_mount(webhook_service):
    container = MagicMock()
    container.attrs = {'Mounts': []}
    with pytest.raises(ValueError, match="No volume or bind mount found mounted on /app"):
        webhook_service.get_volume_name(container)


def test_execute_host_command_success(webhook_service):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = None
        webhook_service.execute_host_command('mock_volume', ['echo', 'Hello'])
        mock_run.assert_called_once_with([
            'docker', 'run', '--rm',
            '-v', 'mock_volume:/app',
            '-v', '/var/run/docker.sock:/var/run/docker.sock',
            '-w', '/app',
            'echo', 'Hello'
        ], check=True)


def test_execute_host_command_failure(webhook_service):
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "command")

        with pytest.raises(InternalServerError) as exc_info:
            webhook_service.execute_host_command('mock_volume', ['echo', 'Hello'])

    assert "Host command failed: Command 'command' returned non-zero exit status 1." in str(exc_info.value)


def test_execute_container_command_success(webhook_service, mock_container):
    mock_container.exec_run.return_value = (0, b'Success')
    output = webhook_service.execute_container_command(mock_container, 'ls')
    assert output == 'Success'
    mock_container.exec_run.assert_called_once_with('ls', workdir='/app')


def test_execute_container_command_failure(webhook_service, mock_container):
    mock_container.exec_run.return_value = (1, b'Error')
    with pytest.raises(InternalServerError) as exc_info:
        webhook_service.execute_container_command(mock_container, 'ls')

    assert "Container command failed: Error" in str(exc_info.value)


def test_log_deployment(webhook_service, mock_container):
    with patch.object(webhook_service, 'execute_container_command') as mock_execute:
        webhook_service.log_deployment(mock_container)
        expected_log_entry = "Deployment successful at"
        mock_execute.assert_called_once()
        assert expected_log_entry in mock_execute.call_args[0][1]


def test_restart_container(webhook_service, mock_container):
    with patch("subprocess.Popen") as mock_popen:
        webhook_service.restart_container(mock_container)
        mock_popen.assert_called_once_with(["/bin/sh", "/app/scripts/restart_container.sh", mock_container.id])
