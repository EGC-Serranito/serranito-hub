import pytest

from app.modules.auth.services import AuthenticationService
from app.modules.auth.repositories import UserRepository
from app.modules.profile.repositories import UserProfileRepository
from unittest.mock import patch, MagicMock
from itsdangerous import SignatureExpired, BadTimeSignature


def test_service_create_with_profie_success(test_app, clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "service_test@example.com",
        "password": "test1234",
        "email_verified": True
    }

    AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 1
    assert UserProfileRepository().count() == 1


def test_service_create_with_profile_fail_no_email(test_app, clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "",
        "password": "1234",
        "email_verified": True
    }

    with pytest.raises(ValueError, match="Email is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_service_create_with_profile_fail_no_name(test_app, clean_database):
    data = {
        "name": "",
        "surname": "Foo",
        "email": "service_test@example.com",
        "password": "1234",
        "email_verified": True
    }

    with pytest.raises(ValueError, match="Name is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_service_create_with_profile_fail_no_surname(test_app, clean_database):
    data = {
        "name": "Test",
        "surname": "",
        "email": "service_test@example.com",
        "password": "1234",
        "email_verified": True
    }

    with pytest.raises(ValueError, match="Surname is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_service_create_with_profile_fail_no_password(test_app, clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "service_test@example.com",
        "password": "",
        "email_verified": True
    }

    with pytest.raises(ValueError, match="Password is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_update_profile_success():
    mock_form = MagicMock()
    mock_form.validate.return_value = True
    mock_form.data = {"name": "NewName", "surname": "NewSurname"}

    with patch("app.modules.auth.services.AuthenticationService.update", return_value="UpdatedInstance") as mock_update:
        service = AuthenticationService()
        result, errors = service.update_profile(1, mock_form)

        assert result == "UpdatedInstance"
        assert errors is None
        mock_update.assert_called_once_with(1, name="NewName", surname="NewSurname")


def test_update_profile_fail_validation():
    mock_form = MagicMock()
    mock_form.validate.return_value = False
    mock_form.errors = {"name": ["This field is required."]}

    service = AuthenticationService()
    result, errors = service.update_profile(1, mock_form)

    assert result is None
    assert errors == {"name": ["This field is required."]}


def test_temp_folder_by_user():
    with patch("app.modules.auth.services.uploads_folder_name", return_value="/uploads"):
        service = AuthenticationService()
        mock_user = MagicMock(id=1)

        folder = service.temp_folder_by_user(mock_user)
        assert folder == "/uploads/temp/1"


def test_confirm_user_with_expired_token():
    with patch("app.modules.auth.services.URLSafeTimedSerializer.loads", side_effect=SignatureExpired("Token expired")):
        service = AuthenticationService()
        with pytest.raises(Exception, match="The confirmation link has expired."):
            service.confirm_user_with_token("expired_token")


def test_confirm_user_with_tampered_token():
    with patch("app.modules.auth.services.URLSafeTimedSerializer.loads", side_effect=BadTimeSignature("Invalid token")):
        service = AuthenticationService()
        with pytest.raises(Exception, match="The confirmation link has been tampered with."):
            service.confirm_user_with_token("tampered_token")