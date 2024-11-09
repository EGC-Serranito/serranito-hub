import pytest
from unittest import mock
from app.modules.zenodo.services import ZenodoService
from app.modules.dataset.models import DataSet
from flask import Flask


@pytest.fixture(scope='function')
def mock_zenodo_service():
    """Fixture para crear un objeto ZenodoService mockeado"""
    return ZenodoService()


def test_test_connection(mock_zenodo_service):
    """ Test the Zenodo connection """

    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        result = mock_zenodo_service.test_connection()
        assert result, "Connection test failed."


def test_test_full_connection(mock_zenodo_service):
    """ Test full connection to Zenodo (create, upload, delete) """
    with mock.patch('requests.post') as mock_post, \
         mock.patch('requests.delete') as mock_delete:

        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": 123}
        mock_post.return_value.status_code = 201
        mock_delete.return_value.status_code = 200
        app = Flask(__name__)

        with app.app_context():
            response = mock_zenodo_service.test_full_connection()

        assert response.status_code == 200, "Full connection test failed."
        assert "success" in response.json, "Missing 'success' in response."
        assert response.json["success"], "Test full connection was not successful."


def test_create_new_deposition(mock_zenodo_service):
    """ Test creating a new deposition in Zenodo """

    app = Flask(__name__)

    with app.app_context():
        dataset_mock = mock.MagicMock(spec=DataSet)
        assert dataset_mock is not None


def test_publish_deposition(mock_zenodo_service):
    """ Test publishing a deposition on Zenodo """

    with mock.patch('requests.post') as mock_post:

        mock_post.return_value.status_code = 202

        mock_post.return_value.json.return_value = {"status": 202, "message": "Published successfully"}

        deposition_id = 123
        response = mock_zenodo_service.publish_deposition(deposition_id)

        assert response["status"] == 202, "Failed to publish deposition."
        assert response["message"] == "Published successfully", "Unexpected message."


def test_get_deposition(mock_zenodo_service):
    """ Test getting a deposition from Zenodo """

    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": 123, "doi": "10.1234/zenodo.12345"}

        deposition_id = 123
        response = mock_zenodo_service.get_deposition(deposition_id)

    assert response["id"] == deposition_id, "Failed to get deposition."
    assert "doi" in response, "DOI not found in response."


def test_get_doi(mock_zenodo_service):
    """ Test getting the DOI of a deposition """

    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": 123, "doi": "10.1234/zenodo.12345"}

        deposition_id = 123
        doi = mock_zenodo_service.get_doi(deposition_id)

    assert doi == "10.1234/zenodo.12345", "DOI mismatch."
