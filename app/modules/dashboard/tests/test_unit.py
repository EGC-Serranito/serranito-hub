from unittest.mock import patch, MagicMock
from app.modules.dashboard.services import DashBoardService
from datetime import datetime
from app import create_app
from app.modules.dashboard.repositories import DashboardRepository
from sqlalchemy.orm.query import Query
import pytest


# Test para 'get_all_author_names_and_dataset_counts'
@pytest.fixture
def dashboard_repository():
    app = create_app()
    with app.app_context():
        repository = DashboardRepository()
        yield repository 


# Test de 'get_all_author_names_and_dataset_counts' para cubrirlo en el repository
def test_get_all_author_names_and_dataset_counts_repository(dashboard_repository):
    # Simula los datos que debería devolver la base de datos como una lista de tuplas
    mock_author_data = [
        ('author1', 1),  # Tupla con nombre de autor y cantidad de datasets
        ('author2', 2),
    ]

    # Mock del método 'all' para simular el comportamiento de la consulta
    with patch.object(Query, 'all', return_value=mock_author_data):
        # Llamamos al método del repositorio a probar
        result = dashboard_repository.get_author_names_and_dataset_counts()

        # Imprimimos el resultado para verificar
        print(result)

        # Verificamos que el resultado sea el esperado
        assert result == [('author1', 1), ('author2', 2)]
        Query.all.assert_called_once()  # Verificamos que 'all' fue llamado una vez


def test_get_all_author_names_and_dataset_counts():
    mock_author_data = [
        ('author1', 1),  # Tupla con nombre de autor y cantidad de datasets
        ('author2', 2),
    ]

    # Mock del repository DashBoardRepository
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_author_names_and_dataset_counts', 
               return_value=mock_author_data):
        dashboard_service = DashBoardService()

        # Llamamos al método a probar
        author_names, dataset_counts = dashboard_service.get_all_author_names_and_dataset_counts()

        assert author_names == ['author1', 'author2']
        assert dataset_counts == [1, 2]


def test_get_all_author_names_and_view_counts():
    # Simula los datos que debería devolver la base de datos
    mock_author_data = [
        ('author1', 5),  # Tupla con nombre de autor y cantidad de datasets
        ('author2', 0),
    ]

    # Mock del repository DashBoardRepository
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_author_names_and_view_counts', 
               return_value=mock_author_data):
        dashboard_service = DashBoardService()

        # Llamamos al método a probar
        author_names, view_counts = dashboard_service.get_all_author_names_and_view_counts()

        assert author_names == ['author1', 'author2']
        assert view_counts == [5, 0]


def test_get_datasets_and_total_sizes():
    # Simula los datos que debería devolver la base de datos
    mock_datasets = [
        MagicMock(name='dataset1', feature_models=[MagicMock(files=[MagicMock(size=100), MagicMock(size=200)])]),
        MagicMock(name='dataset2', feature_models=[MagicMock(files=[MagicMock(size=300), MagicMock(size=400)])]),
    ]

    # Asignar el método 'name' para que se comporte como un método
    mock_datasets[0].name = MagicMock(return_value='dataset1')
    mock_datasets[1].name = MagicMock(return_value='dataset2')

    # Mock del repository DataSetRepository
    with patch('app.modules.dataset.repositories.DataSetRepository.get_all_datasets',
               return_value=mock_datasets):
        dashboard_service = DashBoardService()

        # Llamamos al método a probar
        dataset_names, total_sizes = dashboard_service.get_datasets_and_total_sizes()

        # Verificamos que los resultados sean correctos
        assert dataset_names == ['dataset1', 'dataset2']
        assert total_sizes == [300, 700]  # 100+200 y 300+400


def test_get_views_over_time_with_filter():
    # Simula los datos que debería devolver la base de datos
    mock_result = [
        MagicMock(view_dates='2021-01-01', view_counts_over_time=5),
        MagicMock(view_dates='2021-01-02', view_counts_over_time=0),
    ]

    # Mock del repository DashboardRepository
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_views_over_time',
               return_value=mock_result):
        dashboard_service = DashBoardService()

        # Llamamos al método a probar
        dates, view_counts = dashboard_service.get_views_over_time_with_filter()

        # Verificamos que los resultados sean correctos
        assert dates == ['2021-01-01', '2021-01-02']
        assert view_counts == [5, 0]


def test_get_views_over_time_with_filter_empty_result():
    # Mock del repository DashboardRepository
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_views_over_time',
               return_value=[]):
        dashboard_service = DashBoardService()

        # Llamamos al método a probar
        dates, view_counts = dashboard_service.get_views_over_time_with_filter()

        # Verificamos que los resultados sean correctos
        assert dates == []
        assert view_counts == []


def test_get_publication_types_data():
    # Simula los datos que debería devolver la base de datos
    mock_result = [
        ('type1', 5),
        ('type2', 0),
    ]

    # Mock del repository DashboardRepository
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_publication_types_count',
               return_value=mock_result):
        dashboard_service = DashBoardService()

        # Llamamos al método a probar
        publication_types_count = dashboard_service.get_publication_types_data()

        # Verificamos que los resultados sean correctos
        assert publication_types_count == {'type1': 5, 'type2': 0}


def test_get_downloads_by_day():
    # Simula los datos que debería devolver la base de datos
    mock_result = [
        MagicMock(download_date=datetime(2021, 1, 1), download_count=5),  # Usamos datetime en lugar de cadena
        MagicMock(download_date=datetime(2021, 1, 2), download_count=0),  # Usamos datetime en lugar de cadena
    ]

    # Mock del repository DashboardRepository
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_downloads_by_day_data',
               return_value=mock_result):
        dashboard_service = DashBoardService()

        # Llamamos al método a probar
        downloads_by_day = dashboard_service.get_downloads_by_day()

        # Verificamos que los resultados sean correctos
        assert downloads_by_day == {'2021-01-01': 5, '2021-01-02': 0}
