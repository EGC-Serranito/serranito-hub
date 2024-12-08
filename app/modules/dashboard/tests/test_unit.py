from unittest.mock import patch, MagicMock
from app.modules.dashboard.services import DashBoardService
from datetime import datetime
from app import create_app
from app.modules.dashboard.repositories import DashboardRepository
from sqlalchemy.orm.query import Query
import pytest


@pytest.fixture
def dashboard_repository():
    app = create_app()
    with app.app_context():
        repository = DashboardRepository()
        yield repository


def test_repository_get_all_author_names_and_dataset_counts(dashboard_repository):
    mock_author_data = [
        ('author1', 1),
        ('author2', 2),
    ]

    with patch.object(Query, 'all', return_value=mock_author_data):
        result = dashboard_repository.get_author_names_and_dataset_counts()
        assert result == [('author1', 1), ('author2', 2)]
        Query.all.assert_called_once()


def test_service_get_all_author_names_and_dataset_counts():
    mock_author_data = [
        ('author1', 1),
        ('author2', 2),
    ]
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_author_names_and_dataset_counts',
               return_value=mock_author_data):
        dashboard_service = DashBoardService()
        author_names, dataset_counts = dashboard_service.get_all_author_names_and_dataset_counts()
        assert author_names == ['author1', 'author2']
        assert dataset_counts == [1, 2]


def test_repository_get_all_author_names_and_view_counts(dashboard_repository):
    mock_author_data = [
        ('author1', 5),
        ('author2', 3),
    ]
    with patch.object(Query, 'all', return_value=mock_author_data):
        result = dashboard_repository.get_author_names_and_view_counts()
        assert result == [('author1', 5), ('author2', 3)]
        Query.all.assert_called_once()


def test_service_get_all_author_names_and_view_counts():
    mock_author_data = [
        ('author1', 5),
        ('author2', 0),
    ]
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_author_names_and_view_counts',
               return_value=mock_author_data):
        dashboard_service = DashBoardService()
        author_names, view_counts = dashboard_service.get_all_author_names_and_view_counts()
        assert author_names == ['author1', 'author2']
        assert view_counts == [5, 0]


def test_service_get_datasets_and_total_sizes():
    mock_datasets = [
        MagicMock(name='dataset1', feature_models=[MagicMock(files=[MagicMock(size=100), MagicMock(size=200)])]),
        MagicMock(name='dataset2', feature_models=[MagicMock(files=[MagicMock(size=300), MagicMock(size=400)])]),
    ]
    mock_datasets[0].name = MagicMock(return_value='dataset1')
    mock_datasets[1].name = MagicMock(return_value='dataset2')
    with patch('app.modules.dataset.repositories.DataSetRepository.get_all_datasets',
               return_value=mock_datasets):
        dashboard_service = DashBoardService()
        dataset_names, total_sizes = dashboard_service.get_datasets_and_total_sizes()
        assert dataset_names == ['dataset1', 'dataset2']
        assert total_sizes == [300, 700]  # 100+200 y 300+400


def test_repository_get_views_over_time_with_filter(dashboard_repository):
    mock_result = [
        ('2024-01-01', 10),
        ('2024-01-02', 5),
    ]
    with patch.object(Query, 'all', return_value=mock_result) as mock_all:
        result_day = dashboard_repository.get_views_over_time(filter_type="day")
        assert result_day == [('2024-01-01', 10), ('2024-01-02', 5)]
        result_month = dashboard_repository.get_views_over_time(filter_type="month")
        assert result_month == [('2024-01-01', 10), ('2024-01-02', 5)]
        result_year = dashboard_repository.get_views_over_time(filter_type="year")
        assert result_year == [('2024-01-01', 10), ('2024-01-02', 5)]
        assert mock_all.call_count == 3


def test_service_get_views_over_time_with_filter():
    mock_result = [
        MagicMock(view_dates='2021-01-01', view_counts_over_time=5),
        MagicMock(view_dates='2021-01-02', view_counts_over_time=0),
    ]
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_views_over_time',
               return_value=mock_result):
        dashboard_service = DashBoardService()
        dates, view_counts = dashboard_service.get_views_over_time_with_filter()
        assert dates == ['2021-01-01', '2021-01-02']
        assert view_counts == [5, 0]


def test_repository_get_publication_types_count(dashboard_repository):
    mock_result = [
        ('article', 5),
        ('book', 3),
    ]
    with patch.object(Query, 'all', return_value=mock_result) as mock_all:
        result = dashboard_repository.get_publication_types_count()
        assert result == [('article', 5), ('book', 3)]
        mock_all.assert_called_once()


def test_service_get_publication_types_data():
    mock_result = [
        ('type1', 5),
        ('type2', 0),
    ]
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_publication_types_count',
               return_value=mock_result):
        dashboard_service = DashBoardService()
        publication_types_count = dashboard_service.get_publication_types_data()
        assert publication_types_count == {'type1': 5, 'type2': 0}


def test_repository_get_downloads_by_day_data(dashboard_repository):
    mock_result = [
        ('2024-01-01', 10),
        ('2024-01-02', 5),
    ]
    with patch.object(Query, 'all', return_value=mock_result) as mock_all:
        result = dashboard_repository.get_downloads_by_day_data()
        assert result == [('2024-01-01', 10), ('2024-01-02', 5)]
        mock_all.assert_called_once()


def test_service_get_downloads_by_day():
    mock_result = [
        MagicMock(download_date=datetime(2021, 1, 1), download_count=5),  # Usamos datetime en lugar de cadena
        MagicMock(download_date=datetime(2021, 1, 2), download_count=0),  # Usamos datetime en lugar de cadena
    ]
    with patch('app.modules.dashboard.repositories.DashboardRepository.get_downloads_by_day_data',
               return_value=mock_result):
        dashboard_service = DashBoardService()
        downloads_by_day = dashboard_service.get_downloads_by_day()
        assert downloads_by_day == {'2021-01-01': 5, '2021-01-02': 0}


@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    with app.test_client() as client:
        yield client


def test_get_dashboard_data(test_client):
    mock_author_names_dataset = ['author1', 'author2']
    mock_dataset_counts = [10, 5]
    mock_author_names_view = ['author1', 'author2']
    mock_view_counts = [100, 50]
    mock_dataset_names = ['dataset1', 'dataset2']
    mock_total_sizes = [1000, 500]
    mock_view_dates = ['2024-01-01', '2024-01-02']
    mock_view_counts_over_time = [200, 150]
    mock_publication_types_count = {'article': 5, 'book': 3}
    mock_download_counts = {'2024-01-01': 20, '2024-01-02': 15}

    with patch('app.modules.dashboard.services.DashBoardService.get_all_author_names_and_dataset_counts',
               return_value=(mock_author_names_dataset, mock_dataset_counts)), \
         patch('app.modules.dashboard.services.DashBoardService.get_all_author_names_and_view_counts',
               return_value=(mock_author_names_view, mock_view_counts)), \
         patch('app.modules.dashboard.services.DashBoardService.get_datasets_and_total_sizes',
               return_value=(mock_dataset_names, mock_total_sizes)), \
         patch('app.modules.dashboard.services.DashBoardService.get_views_over_time_with_filter',
               return_value=(mock_view_dates, mock_view_counts_over_time)), \
         patch('app.modules.dashboard.services.DashBoardService.get_publication_types_data',
               return_value=mock_publication_types_count), \
         patch('app.modules.dashboard.services.DashBoardService.get_downloads_by_day',
               return_value=mock_download_counts):

        response = test_client.get('/dashboard')

        assert response.status_code == 200
        assert b'author1' in response.data
        assert b'author2' in response.data
        assert b'2024-01-01' in response.data
        assert b'200' in response.data
