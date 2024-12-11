from unittest.mock import MagicMock
import pytest

from app.modules.featuremodel.services import FeatureModelService


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


def test_sample_assertion(test_client):
    """
    Sample test to verify that the test framework and environment are working correctly.
    It does not communicate with the Flask application; it only performs a simple assertion to
    confirm that the tests in this module can be executed.
    """
    greeting = "Hello, World!"
    assert (
        greeting == "Hello, World!"
    ), "The greeting does not coincide with 'Hello, World!'"


@pytest.fixture
def mock_hubfile_service():
    """
    Creates a mock for the HubfileService to simulate total views and downloads.
    """
    hubfile_service = MagicMock()
    hubfile_service.total_hubfile_views.return_value = 100
    hubfile_service.total_hubfile_downloads.return_value = 50
    return hubfile_service


def test_total_feature_model_views(mock_hubfile_service):
    """
    Test the total_feature_model_views method of FeatureModelService.
    Ensures it correctly returns the total number of views using the mocked service.
    """
    service = FeatureModelService()
    service.hubfile_service = mock_hubfile_service
    assert service.total_feature_model_views() == 100, "The total views should be 100."


def test_total_feature_model_downloads(mock_hubfile_service):
    """
    Test the total_feature_model_downloads method of FeatureModelService.
    Ensures it correctly returns the total number of downloads using the mocked service.
    """
    service = FeatureModelService()
    service.hubfile_service = mock_hubfile_service
    assert service.total_feature_model_downloads() == 50, "The total downloads should be 50."


def test_count_feature_models():
    """
    Test the count_feature_models method of FeatureModelService.
    Verifies that the method correctly interacts with the repository and returns the count
    of feature models.
    """
    service = FeatureModelService()

    mock_repository = MagicMock()
    mock_repository.count_feature_models.return_value = 42

    service.repository = mock_repository

    result = service.count_feature_models()
    assert result == 42, "The count of feature models should be 42."

    mock_repository.count_feature_models.assert_called_once()
