import pytest

from app.modules.auth.services import AuthenticationService
from app.modules.auth.repositories import UserRepository
from app.modules.profile.repositories import UserProfileRepository


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


def test_service_create_with_profile_fail_no_password(test_app, clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "test@example.com",
        "password": "",
        "email_verified": True
    }

    with pytest.raises(ValueError, match="Password is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_is_email_available(test_app, clean_database):
    data = {
        "name": "Test",
        "surname": "User",
        "email": "testuser@example.com",
        "password": "test1234",
        "email_verified": True
    }
    auth_service = AuthenticationService()
    auth_service.create_with_profile(**data)

    available = auth_service.is_email_available("testuser@example.com")
    assert available is False

    available = auth_service.is_email_available("newuser@example.com")
    assert available is True


def test_confirm_user_with_token(test_app, clean_database):
    # Crear un usuario
    data = {
        "name": "Test",
        "surname": "User",
        "email": "testuser@example.com",
        "password": "test1234",
        "email_verified": False
    }
    auth_service = AuthenticationService()
    auth_service.create_with_profile(**data)

    token = auth_service.get_token_from_email("testuser@example.com")

    confirmed_user = auth_service.confirm_user_with_token(token)

    assert confirmed_user.email_verified is True