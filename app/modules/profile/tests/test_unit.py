import pytest
from unittest.mock import MagicMock, patch
from app.modules.profile.services import UserProfileService
from app.modules.profile.repositories import UserProfileRepository


@pytest.fixture
def mock_user_profile_repo():
    """Mock de UserProfileRepository."""
    with patch.object(UserProfileRepository, 'update', return_value="user_updated") as mock_update:
        yield mock_update


@pytest.fixture
def mock_form():
    """Mock de un formulario."""
    form_mock = MagicMock()
    form_mock.validate.return_value = True  # Simulamos que la validación fue exitosa
    form_mock.data = {'name': 'John Doe', 'age': 30}  # Datos del formulario
    return form_mock


@pytest.fixture
def user_profile_service():
    """Instancia del servicio con el repositorio mockeado."""
    return UserProfileService()


def test_update_profile_success(user_profile_service, mock_user_profile_repo, mock_form):
    """Test exitoso de update_profile cuando la validación es correcta."""
    user_profile_id = 1
    updated_instance, errors = user_profile_service.update_profile(user_profile_id, mock_form)

    mock_user_profile_repo.assert_called_once_with(user_profile_id, **mock_form.data)
    assert updated_instance == "user_updated"
    assert errors is None


def test_update_profile_failure(user_profile_service, mock_form):
    """Test para verificar que ocurre cuando la validación falla en el formulario."""
    mock_form.validate.return_value = False
    mock_form.errors = {'name': ['This field is required.']}

    user_profile_id = 1
    updated_instance, errors = user_profile_service.update_profile(user_profile_id, mock_form)

    assert updated_instance is None
    assert errors == {'name': ['This field is required.']}