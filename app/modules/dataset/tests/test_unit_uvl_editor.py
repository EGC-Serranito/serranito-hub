import pytest
from unittest import mock
from app.modules.dataset.models import DataSet
from app.modules.dataset.services import DataSetService
from app import create_app


@pytest.fixture(scope="function")
def service():
    # app = create_app()
    # app_context = app.app_context()
    # app_context.push()
    service = DataSetService()
    service.dsmetadata_repository = mock.MagicMock()
    service.author_repository = mock.MagicMock()
    service.feature_model_repository = mock.MagicMock()
    service.fmmetadata_repository = mock.MagicMock()
    service.hubfilerepository = mock.MagicMock()
    service.repository = mock.MagicMock()
    service.create = mock.MagicMock()

    def mock_create(**kwargs):
        res = DataSet()
        res.commit = kwargs.get("commit", None)
        res.version = kwargs.get("version", None)
        res.user_id = kwargs.get("user_id", None)
        res.ds_meta_data_id = kwargs.get("ds_meta_data_id", None)
        res.last_version_id = kwargs.get("last_version_id", None)
        return res

    service.create.side_effect = mock_create
    return service


@pytest.fixture(scope="function")
def mock_form():
    app = create_app()
    with app.app_context():
        form = mock.MagicMock()
        form.get_dsmetadata.return_value = {
            "title": "Test Dataset",
            "description": "Test Description",
        }
        form.get_authors.return_value = [
            {"name": "Author1", "affiliation": "Affiliation1", "orcid": "ORCID1"},
            {"name": "Author2", "affiliation": "Affiliation2", "orcid": "ORCID2"},
        ]
        form.feature_models = [mock.MagicMock()]
        form.feature_models[0].uvl_filename.data = "test_file.uvl"
        form.feature_models[0].get_fmmetadata.return_value = {
            "title": "Test FMMetadata",
        }
        form.feature_models[0].get_authors.return_value = [
            {"name": "FM Author", "affiliation": "FM Affiliation", "orcid": "FM ORCID"},
        ]
        return form


@pytest.fixture(scope="function")
def mock_user():
    app = create_app()
    with app.app_context():
        user = mock.MagicMock()
        user.profile.surname = "Doe"
        user.profile.name = "John"
        user.profile.affiliation = "Test Affiliation"
        user.profile.orcid = "ORCID1234"
        user.temp_folder.return_value = "/tmp/test_user"
        return user


@pytest.fixture(scope="function")
def mock_dataset():
    app = create_app()
    with app.app_context():
        dataset = mock.MagicMock(spec=DataSet)
        dataset.id = 1
        dataset.version = 1
        return dataset


@mock.patch(
    "app.modules.dataset.services.calculate_checksum_and_size",
    return_value=("checksum123", 1024),
)
def test_update_from_form_success(
    mock_calculate_checksum, service, mock_form, mock_user, mock_dataset
):
    with mock.patch("app.modules.dataset.services.DataSet.query") as mock_query:
        mock_query.filter.return_value.order_by.return_value.all.return_value = [
            mock_dataset
        ]

        updated_dataset = service.update_from_form(
            form=mock_form,
            current_user=mock_user,
            last_dataset_id=1,
        )

        service.dsmetadata_repository.create.assert_called_once_with(
            **mock_form.get_dsmetadata()
        )
        service.author_repository.create.assert_called()
        service.feature_model_repository.create.assert_called()
        service.fmmetadata_repository.create.assert_called()
        service.hubfilerepository.create.assert_called()
        service.repository.session.commit.assert_called_once()
        assert updated_dataset.version == mock_dataset.version + 1
        assert updated_dataset.last_version_id == mock_dataset.id


def test_update_from_form_exception(service, mock_form, mock_user):
    service.dsmetadata_repository.create.side_effect = Exception("Test Exception")

    with pytest.raises(Exception, match="Test Exception"):
        service.update_from_form(
            form=mock_form,
            current_user=mock_user,
            last_dataset_id=1,
        )

    service.repository.session.rollback.assert_called_once()
    service.repository.session.commit.assert_not_called()


@mock.patch(
    "app.modules.dataset.services.calculate_checksum_and_size",
    return_value=("checksum123", 1024),
)
def test_update_from_form_no_previous_versions(
    mock_calculate_checksum, service, mock_form, mock_user
):
    with mock.patch("app.modules.dataset.services.DataSet.query") as mock_query:
        mock_query.filter.return_value.order_by.return_value.all.return_value = []

        with pytest.raises(
            ValueError, match="If last_dataset_id is None, you must to do create"
        ):
            service.update_from_form(
                form=mock_form,
                current_user=mock_user,
                last_dataset_id=None,
            )

        service.repository.session.rollback.assert_called_once()
        service.repository.session.commit.assert_not_called()


@mock.patch(
    "app.modules.dataset.services.calculate_checksum_and_size",
    return_value=("checksum123", 1024),
)
def test_update_from_form_invalid_form_data(
    mock_calculate_checksum, service, mock_form, mock_user
):
    mock_form.get_dsmetadata.return_value = None

    with pytest.raises(TypeError, match="DsMetadata can't be None"):
        service.update_from_form(
            form=mock_form,
            current_user=mock_user,
            last_dataset_id=1,
        )

    service.repository.session.rollback.assert_called_once()
