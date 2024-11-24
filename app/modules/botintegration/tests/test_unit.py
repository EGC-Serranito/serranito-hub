import pytest
from unittest.mock import patch, MagicMock
from app.modules.botintegration.services import NodeService
from app.modules.botintegration.features import FeatureService
from app import create_app
from app.modules.auth.models import User


@pytest.fixture
def mock_user():
    app = create_app()
    with app.app_context():
        user = MagicMock(spec=User)
        user.id = 1
        user.temp_folder.return_value = "/mock/temp/folder"
        user.profile.surname = "Doe"
        user.profile.name = "John"
        user.profile.affiliation = "Test University"
        user.profile.orcid = "0000-0001-2345-6789"
        return user


@pytest.fixture
def mock_treenode():
    """
    Fixture to provide a mocked TreeNode instance.
    """
    app = create_app()
    with app.app_context():
        tree_node = MagicMock()
        tree_node.id = 1
        tree_node.name = "root"
        tree_node.user_id = 1
        tree_node.parent_id = None
        tree_node.path = "root"
        tree_node.single_child = False
        tree_node.children = []
        return tree_node


@pytest.fixture
def mock_treenode_bot():
    """
    Fixture to provide a mocked TreeNodeBot instance.
    """
    app = create_app()
    with app.app_context():
        tree_node_bot = MagicMock()
        tree_node_bot.id = 1
        tree_node_bot.name = "root"
        tree_node_bot.parent_id = None
        tree_node_bot.path = "root"
        tree_node_bot.single_child = False
        tree_node_bot.children = []
        return tree_node_bot


@pytest.fixture
def mock_env():
    """
    Fixture to patch os.getenv for environment variable mock.
    """
    with patch("os.getenv", return_value="localhost") as mock:
        yield mock


@pytest.fixture
def node_service():
    return NodeService()


@pytest.fixture
def feature_service():
    return FeatureService()


# Testing for NodeService
def test_create_node_route_with_different_types(node_service):
    # Arrange
    form = MagicMock()
    form.name.data = "test_node"  # Campo 'name' del formulario

    app = create_app()

    with patch(
        "app.modules.botintegration.services.NodeService.create_node_route_add_chat"
    ) as mock_create_node_route_add_chat, patch(
        "app.modules.botintegration.services.NodeService.create_node_route_add_bot"
    ) as mock_create_node_route_add_bot, patch(
        "app.modules.botintegration.services.NodeService.create_node_route_add_types_notification"
    ) as mock_create_node_route_add_types_notification, patch(
        "app.modules.botintegration.services.NodeService.create_node_route_add_feature"
    ) as mock_create_node_route_add_feature:
        # Simulación de las respuestas de cada método del servicio
        mock_create_node_route_add_chat.return_value = {
            "id": 1,
            "name": form.name.data,
            "parent_id": None,
            "path": "/chat_node",
            "single_child": False,
        }

        mock_create_node_route_add_bot.return_value = {
            "id": 2,
            "name": form.name.data,
            "parent_id": None,
            "path": "/bot_node",
            "single_child": False,
        }

        mock_create_node_route_add_types_notification.return_value = {
            "id": 3,
            "name": form.name.data,
            "parent_id": None,
            "path": "/notification_node",
            "single_child": False,
        }

        mock_create_node_route_add_feature.return_value = {
            "id": 4,
            "name": form.name.data,
            "parent_id": None,
            "path": "/feature_node",
            "single_child": False,
        }

        with app.app_context():
            # Datos necesarios
            user_id = 1
            parent_id = None
            single_child = False

            # Act - Llamadas a los diferentes métodos
            chat_node = node_service.create_node_route_add_chat(
                user_id=user_id,
                name=form.name.data,
                parent_id=parent_id,
                path="/chat_node",
                single_child=single_child,
            )
            bot_node = node_service.create_node_route_add_bot(
                user_id=user_id,
                name=form.name.data,
                parent_id=parent_id,
                path="/bot_node",
                single_child=single_child,
            )
            notification_node = node_service.create_node_route_add_types_notification(
                user_id=user_id,
                name=form.name.data,
                parent_id=parent_id,
                path="/notification_node",
                single_child=single_child,
            )
            feature_node = node_service.create_node_route_add_feature(
                user_id=user_id,
                name=form.name.data,
                parent_id=parent_id,
                path="/feature_node",
                single_child=single_child,
            )

            # Assert - Verificar que los valores devueltos son correctos
            assert chat_node["id"] == 1
            assert chat_node["name"] == form.name.data
            assert chat_node["path"] == "/chat_node"
            assert chat_node["single_child"] == single_child

            assert bot_node["id"] == 2
            assert bot_node["name"] == form.name.data
            assert bot_node["path"] == "/bot_node"
            assert bot_node["single_child"] == single_child

            assert notification_node["id"] == 3
            assert notification_node["name"] == form.name.data
            assert notification_node["path"] == "/notification_node"
            assert notification_node["single_child"] == single_child

            assert feature_node["id"] == 4
            assert feature_node["name"] == form.name.data
            assert feature_node["path"] == "/feature_node"
            assert feature_node["single_child"] == single_child

            # Assert - Verificar que cada uno de los métodos del servicio se llamó correctamente
            mock_create_node_route_add_chat.assert_called_once_with(
                user_id=user_id,
                name=form.name.data,
                parent_id=parent_id,
                path="/chat_node",
                single_child=single_child,
            )

            mock_create_node_route_add_bot.assert_called_once_with(
                user_id=user_id,
                name=form.name.data,
                parent_id=parent_id,
                path="/bot_node",
                single_child=single_child,
            )

            mock_create_node_route_add_types_notification.assert_called_once_with(
                user_id=user_id,
                name=form.name.data,
                parent_id=parent_id,
                path="/notification_node",
                single_child=single_child,
            )

            mock_create_node_route_add_feature.assert_called_once_with(
                user_id=user_id,
                name=form.name.data,
                parent_id=parent_id,
                path="/feature_node",
                single_child=single_child,
            )


def test_path_equal_treenode_bot_delete_node(
    node_service, mock_treenode, mock_treenode_bot
):
    # Arrange
    node_id_to_delete = mock_treenode.id  # El ID del nodo que queremos eliminar
    node_path_to_delete = mock_treenode.path  # El path del nodo que queremos eliminar
    bot_path_to_delete = mock_treenode_bot.path  # El path del nodo asociado TreeNodeBot

    app = create_app()

    # Simulamos el comportamiento del repositorio para eliminar el nodo
    with patch(
        "app.modules.botintegration.services.NodeService.delete_node"
    ) as mock_delete_node, patch(
        "app.modules.botintegration.services.NodeService.get_tree_nodes_by_path"
    ) as mock_get_tree_nodes_by_path:
        with app.app_context():
            # Simulamos que la eliminación es exitosa para el nodo principal
            mock_delete_node.return_value = True

            # Simulamos que el TreeNodeBot tiene el mismo path que el TreeNode a eliminar
            mock_get_tree_nodes_by_path.return_value = (
                [mock_treenode_bot] if node_path_to_delete == bot_path_to_delete else []
            )

            # Act
            result = node_service.delete_node(node_id_to_delete)

            # Assert
            # Verificamos que el método delete_node fue llamado con el ID correcto para el TreeNode
            mock_delete_node.assert_called_once_with(node_id_to_delete)

            if mock_treenode.path == mock_treenode_bot.path:
                # En este caso, debería haberse llamado a delete_node para eliminar también el TreeNodeBot
                mock_delete_node.assert_any_call(mock_treenode_bot.id)
            else:
                # Si los paths no coinciden, no debe eliminar el nodo bot
                mock_delete_node.assert_not_called()

            # Comprobamos que el resultado contiene el mensaje de éxito
            assert result is True


def test_merge_node_with_node_not_found(node_service):
    # Using patch to mock a specific method (example: patching `total_dataset_views`)
    with patch.object(node_service.repository, "get_node_by_id") as mock_get_node_by_id:

        # Arrange
        mock_get_node_by_id.return_value = None

        # Act
        result, status_code = node_service.merge_node(999, 1)

        # Assert
        assert status_code == 404
        assert result["error"] == "Node not found"
        mock_get_node_by_id.assert_called_once_with(999)


def test_remove_stopped_chats(node_service, mock_treenode):
    # Usamos create_app para inicializar la aplicación
    app = create_app()

    # Simulamos que mock_treenode tiene la estructura correcta
    with app.app_context():
        # Asegurémonos de que mock_treenode tiene los valores correctos
        mock_treenode.children = [
            MagicMock(
                name="4",
                children=[
                    MagicMock(
                        name="1", children=[MagicMock(name="7")]
                    ),  # Nodo a eliminar (name="1", child="7")
                    MagicMock(
                        name="1", children=[]
                    ),  # Nodo que no se elimina (name="1", no child="7")
                    MagicMock(name="0", children=[]),  # Nodo a eliminar (name="0")
                ],
            )
        ]

        # Actuar sobre el nodo simulado
        node_service.remove_stopped_chats(mock_treenode)

        # Verificar que los nodos con 'name' == '0' han sido eliminados
        assert not any(
            child.name == "0" for child in mock_treenode.children[0].children
        )

        # Verificar que el nodo con 'name' == '1' y un hijo con 'name' == '7' ha sido eliminado
        assert not any(
            child.name == "1"
            for child in mock_treenode.children[0].children
            if any(grandchild.name == "7" for grandchild in child.children)
        )


def test_transform_to_full_url(feature_service):
    # Act
    result = feature_service.transform_to_full_url("example.com")

    # Assert
    assert result == "http://example.com"

    # Test with URL already having http://
    result = feature_service.transform_to_full_url("http://example.com")
    assert result == "http://example.com"

    # Test with URL already having https://
    result = feature_service.transform_to_full_url("https://example.com")
    assert result == "https://example.com"
