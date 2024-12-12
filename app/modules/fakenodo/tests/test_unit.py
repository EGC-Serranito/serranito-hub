import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_test_connection_fakenodo(client):
    """Test the GET route of test_connection_fakenodo"""
    response = client.get("/fakenodo/api")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["message"] == "Connected to Fakenodo API"


def test_create_fakenodo(client):
    """Test the POST route of create_fakenodo"""
    response = client.post("/fakenodo/api")
    data = response.get_json()
    assert response.status_code == 201
    assert data["status"] == "success"
    assert data["message"] == "Created deposition (Fakenodo API)"


def test_deposition_files_fakenodo(client):
    """Test the POST route of deposition_files_fakenodo"""
    depositionid = "12345"
    response = client.post(f"/fakenodo/api/{depositionid}/files")
    data = response.get_json()
    assert response.status_code == 201
    assert data["status"] == "success"
    assert data["message"] == f"Created deposition with ID {depositionid} (Fakenodo API)"


def test_delete_deposition_fakenodo(client):
    """Test the DELETE route of delete_deposition_fakenodo"""
    depositionid = "12345"
    response = client.delete(f"/fakenodo/api/{depositionid}")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["message"] == f"Deleted deposition with ID {depositionid} (Fakenodo API)"


def test_publish_deposition_fakenodo(client):
    """Test the POST route of publish_deposition_fakenodo"""
    depositionid = "12345"
    response = client.post(f"/fakenodo/api/{depositionid}/actions/publish")
    data = response.get_json()
    assert response.status_code == 202
    assert data["status"] == "success"
    assert data["message"] == f"Published deposition with ID {depositionid} (Fakenodo API)"


def test_get_deposition_fakenodo(client):
    """Test the GET route of get_deposition_fakenodo"""
    depositionid = "12345"
    response = client.get(f"/fakenodo/api/{depositionid}")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["message"] == f"Got deposition with ID {depositionid} (Fakenodo API)"
    assert data["doi"] == "10.5072/fakenodo.123456"
