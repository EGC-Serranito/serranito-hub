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
