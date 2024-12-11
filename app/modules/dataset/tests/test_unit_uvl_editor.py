import unittest
from unittest.mock import MagicMock, patch
from app.modules.dataset.models import DataSet
from app.modules.dataset.services import (
    DataSetService,
)
from app import create_app


class TestUpdateFromForm(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.service = DataSetService()
        self.service.dsmetadata_repository = MagicMock()
        self.service.author_repository = MagicMock()
        self.service.feature_model_repository = MagicMock()
        self.service.fmmetadata_repository = MagicMock()
        self.service.hubfilerepository = MagicMock()
        self.service.repository = MagicMock()
        # Simular el método `create`
        self.service.create = MagicMock()

        # Configurar comportamiento del mock `create`
        def mock_create(**kwargs):
            res = DataSet()
            res.commit = kwargs.get("commit", None)
            res.version = kwargs.get("version", None)
            res.user_id = kwargs.get("user_id", None)
            res.ds_meta_data_id = kwargs.get("ds_meta_data_id", None)
            res.last_version_id = kwargs.get("last_version_id", None)
            return res

        self.service.create.side_effect = mock_create

        self.mock_form = MagicMock()
        self.mock_form.get_dsmetadata.return_value = {
            "title": "Test Dataset",
            "description": "Test Description",
        }
        self.mock_form.get_authors.return_value = [
            {"name": "Author1", "affiliation": "Affiliation1", "orcid": "ORCID1"},
            {"name": "Author2", "affiliation": "Affiliation2", "orcid": "ORCID2"},
        ]

        self.mock_form.feature_models = [MagicMock()]
        self.mock_form.feature_models[0].uvl_filename.data = "test_file.uvl"
        self.mock_form.feature_models[0].get_fmmetadata.return_value = {
            "title": "Test FMMetadata",
        }
        self.mock_form.feature_models[0].get_authors.return_value = [
            {"name": "FM Author", "affiliation": "FM Affiliation", "orcid": "FM ORCID"},
        ]

        self.mock_user = MagicMock()
        self.mock_user.profile.surname = "Doe"
        self.mock_user.profile.name = "John"
        self.mock_user.profile.affiliation = "Test Affiliation"
        self.mock_user.profile.orcid = "ORCID1234"
        self.mock_user.temp_folder.return_value = "/tmp/test_user"

        self.last_dataset_id = 1

        self.mock_dataset = MagicMock(spec=DataSet)
        self.mock_dataset.id = 1
        self.mock_dataset.version = 1

    @patch(
        "app.modules.dataset.services.calculate_checksum_and_size",
        return_value=("checksum123", 1024),
    )
    def test_update_from_form_success(self, mock_calculate_checksum):
        # Configuración del mock de DataSet.query
        with patch("app.modules.dataset.services.DataSet.query") as mock_query:
            mock_query.filter.return_value.order_by.return_value.all.return_value = [
                self.mock_dataset
            ]

            # Llamada al método
            updated_dataset = self.service.update_from_form(
                form=self.mock_form,
                current_user=self.mock_user,
                last_dataset_id=self.last_dataset_id,
            )

            # Verificaciones
            self.service.dsmetadata_repository.create.assert_called_once_with(
                **self.mock_form.get_dsmetadata()
            )
            self.service.author_repository.create.assert_called()
            self.service.feature_model_repository.create.assert_called()
            self.service.fmmetadata_repository.create.assert_called()
            self.service.hubfilerepository.create.assert_called()
            self.service.repository.session.commit.assert_called_once()
            self.assertEqual(updated_dataset.version, self.mock_dataset.version + 1)
            self.assertEqual(updated_dataset.last_version_id, self.mock_dataset.id)

    def test_update_from_form_exception(self):
        # Forzar una excepción
        self.service.dsmetadata_repository.create.side_effect = Exception(
            "Test Exception"
        )

        with self.assertRaises(Exception) as context:
            self.service.update_from_form(
                form=self.mock_form,
                current_user=self.mock_user,
                last_dataset_id=self.last_dataset_id,
            )

        self.assertEqual(str(context.exception), "Test Exception")
        self.service.repository.session.rollback.assert_called_once()
        self.service.repository.session.commit.assert_not_called()

    @patch(
        "app.modules.dataset.services.calculate_checksum_and_size",
        return_value=("checksum123", 1024),
    )
    def test_update_from_form_no_previous_versions(self, mock_calculate_checksum):
        # Simular que no hay versiones anteriores del dataset
        with patch("app.modules.dataset.services.DataSet.query") as mock_query:
            mock_query.filter.return_value.order_by.return_value.all.return_value = []

            # Llamada al método y verificar que lanza excepción
            with self.assertRaises(ValueError) as context:
                self.service.update_from_form(
                    form=self.mock_form,
                    current_user=self.mock_user,
                    last_dataset_id=None,
                )

            # Verificar el mensaje de la excepción
            self.assertEqual(str(context.exception), "If last_dataset_id is None, you must to do create")
            self.service.repository.session.rollback.assert_called_once()
            self.service.repository.session.commit.assert_not_called()

    @patch(
        "app.modules.dataset.services.calculate_checksum_and_size",
        return_value=("checksum123", 1024),
    )
    def test_update_from_form_invalid_form_data(self, mock_calculate_checksum):
        # Configurar el mock del formulario para devolver datos inválidos
        self.mock_form.get_dsmetadata.return_value = None

        with self.assertRaises(TypeError) as context:
            self.service.update_from_form(
                form=self.mock_form,
                current_user=self.mock_user,
                last_dataset_id=self.last_dataset_id,
            )
        self.assertEqual(str(context.exception), "DsMetadata can't be None")
        self.service.repository.session.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
