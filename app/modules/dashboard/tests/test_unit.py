from unittest.mock import patch, MagicMock
from app.modules.dashboard.services import DashBoardService


# Test para 'get_all_author_names_and_dataset_counts'
def test_get_all_author_names_and_dataset_counts():
    # Simula los datos que debería devolver la base de datos
    mock_author_data = [
        MagicMock(name='author1', dataset_count=1),
        MagicMock(name='author2', dataset_count=2),
    ]

    # Asigna el valor correcto a 'name' para cada MagicMock
    mock_author_data[0].name = 'author1'
    mock_author_data[1].name = 'author2'

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
        MagicMock(name='author1', view_count=5),
        MagicMock(name='author2', view_count=0),
    ]

    # Asigna el valor correcto a 'name' para cada MagicMock
    mock_author_data[0].name = 'author1'
    mock_author_data[1].name = 'author2'

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
