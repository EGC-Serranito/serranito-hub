import pytest

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app.modules.dataset.models import DataSet, DSMetaData


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    for module testing (por example, new users)
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


@pytest.fixture(autouse=True)
def ensure_logout(test_client):
    logout(test_client)
    yield
    logout(test_client)


def test_edit_profile_page_get(test_client):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/edit")
    assert response.status_code == 200, "The profile editing page could not be accessed."
    assert b"Edit profile" in response.data, "The expected content is not present on the page"

    logout(test_client)


def test_my_profile_page(test_client):
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    user = User.query.filter_by(email="user@example.com").first()

    ds_meta_data = DSMetaData(
        title="Test Dataset Title",
        description="Test Description",
        publication_type="other",
        tags="tag1,tag2"
    )
    db.session.add(ds_meta_data)
    db.session.commit()

    dataset1 = DataSet(name="Dataset 1", user_id=user.id, ds_meta_data_id=ds_meta_data.id)
    dataset2 = DataSet(name="Dataset 2", user_id=user.id, ds_meta_data_id=ds_meta_data.id)
    db.session.add_all([dataset1, dataset2])
    db.session.commit()


def test_edit_profile_page_unauthenticated(test_client):
    response = test_client.get("/profile/edit")
    assert response.status_code == 302, "Unauthenticated user should be redirected."
    assert response.location == "/login?next=%2Fprofile%2Fedit", "Redirection location should be the login page with the next parameter."


def test_my_profile_page_unauthenticated(test_client):
    response = test_client.get("/profile/summary")
    assert response.status_code == 302, "Unauthenticated user should be redirected."
    assert response.location == "/login?next=%2Fprofile%2Fsummary", "Redirection location should be the login page with the next parameter."
