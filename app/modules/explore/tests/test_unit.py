import pytest
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def test_explore_index_route(client):
    response = client.get('/explore')
    assert response.status_code == 200, "La página de Explore no se cargó correctamente."
    assert b'Explore' in response.data, "El contenido 'Explore' no está presente."


def test_explore_with_valid_filters(client):
    params = {
        "query": "python",
        "sorting": "oldest",
        "publication_type": "datamanagementplan",
        "tags": ["tag1", "tag2"]
    }
    response = client.get('/explore', query_string=params)
    assert response.status_code == 200, "La respuesta a /explore con filtros válidos no fue exitosa."
    assert b'id="results"' in response.data, \
        "El contenedor de resultados no está presente en la respuesta con filtros válidos."


def test_explore_empty_results(client):
    params = {
        "query": "python",
        "sorting": "newest",
        "publication_type": "notype",
        "tags": ["unknown_tag"]
    }
    response = client.get('/explore', query_string=params)
    assert response.status_code == 200, "La respuesta a /explore con una búsqueda sin resultados no fue exitosa."
    assert b'We have not found any datasets that meet your search criteria. ' in response.data, \
        "Se han encontrado resultados."
