import pytest
from flask import url_for
from flask_login import login_user, logout_user
from app.modules.auth.services import AuthenticationService
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Verify user
        token = AuthenticationService().get_token_from_email("test@example.com")
        AuthenticationService().confirm_user_with_token(token)
    yield test_client


def test_login_success(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path != url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_email(test_client):
    response = test_client.post(
        "/login", data=dict(email="bademail@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_password(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="basspassword"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_not_verified(test_client):
    response = test_client.post(
        "/login", data=dict(email="test2@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"


def test_signup_user_no_name(test_client):
    response = test_client.post(
        "/signup", data=dict(surname="Foo", email="test@example.com", password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert b"This field is required" in response.data, response.data


def test_signup_user_unsuccessful(test_client):
    email = "test@example.com"
    response = test_client.post(
        "/signup", data=dict(name="Test", surname="Foo", email=email, password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert f"Email {email} in use".encode("utf-8") in response.data


def test_signup_user_no_verify(test_client):
    response = test_client.post(
        "/signup", data=dict(name="Foo", surname="Example", email="test2@example.com", password="test1234"),
        follow_redirects=True
    )

    assert response.request.path != url_for("public.index"), "Signup was unsuccessful"
    assert b"Check your email to verify your account" in response.data


def test_signup_user_successful(test_client):
    response = test_client.post(
        "/signup",
        data=dict(name="Foo", surname="Example", email="foo@example.com", password="foo1234", email_verified=False),
        follow_redirects=True,
    )
    assert response.request.path != url_for("public.index"), "Signup was unsuccessful"


def test_get_authenticated_user_authenticated(test_app, test_client, clean_database):
    with test_app.app_context():
        user = User(id=1, email="test@example.com", password="password123", email_verified=True)
        login_user(user)

        service = AuthenticationService()
        authenticated_user = service.get_authenticated_user()

        assert authenticated_user == user

        logout_user()


def test_get_authenticated_user_not_authenticated(test_app, test_client):
    with test_app.app_context():

        logout_user()

        service = AuthenticationService()
        result = service.get_authenticated_user()

        assert result is None


def test_get_authenticated_user_profile_authenticated(test_app, test_client):
    with test_app.app_context():
        from flask_login import login_user

        profile = UserProfile(id=1, name="Test", surname="User")
        user = User(id=1, email="test@example.com", password="password123", email_verified=True, profile=profile)

        login_user(user)

        service = AuthenticationService()
        result = service.get_authenticated_user_profile()

        assert result == profile
        assert result.name == "Test"
        assert result.surname == "User"


def test_get_authenticated_user_profile_not_authenticated(test_app, test_client):
    with test_app.app_context():

        logout_user()

        service = AuthenticationService()
        result = service.get_authenticated_user_profile()

        assert result is None
