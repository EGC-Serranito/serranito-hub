import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.modules.botintegration.services import NodeService
from app.modules.botintegration.features import FeatureService
from app import create_app
from app.modules.auth.models import User
import os
import yaml


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


def test_merge_simple_trees(node_service):
    tree1 = {
        "id": 1,
        "name": "root",
        "path": "/root",
        "parent_id": None,
        "single_child": False,
        "children": [],
    }
    tree2 = {
        "id": 2,
        "name": "root",
        "path": "/root",
        "parent_id": None,
        "single_child": False,
        "children": [],
    }

    merged_tree = node_service.merge_nary_trees(tree1, tree2)
    assert merged_tree == tree1  # En este caso, tree1 y tree2 son equivalentes


def test_merge_trees_with_different_children(node_service):
    tree1 = {
        "id": 1,
        "name": "root",
        "path": "/root",
        "parent_id": None,
        "single_child": False,
        "children": [
            {"id": 2, "name": "child1", "path": "/root/child1", "children": []}
        ],
    }
    tree2 = {
        "id": 1,
        "name": "root",
        "path": "/root",
        "parent_id": None,
        "single_child": False,
        "children": [
            {"id": 3, "name": "child2", "path": "/root/child2", "children": []}
        ],
    }

    merged_tree = node_service.merge_nary_trees(tree1, tree2)
    assert len(merged_tree["children"]) == 2
    assert any(child["name"] == "child1" for child in merged_tree["children"])
    assert any(child["name"] == "child2" for child in merged_tree["children"])


def test_merge_trees_with_shared_children(node_service):
    tree1 = {
        "id": 1,
        "name": "root",
        "path": "/root",
        "parent_id": None,
        "single_child": False,
        "children": [
            {"id": 2, "name": "child1", "path": "/root/child1", "children": []}
        ],
    }
    tree2 = {
        "id": 1,
        "name": "root",
        "path": "/root",
        "parent_id": None,
        "single_child": False,
        "children": [
            {"id": 3, "name": "child1", "path": "/root/child1", "children": []}
        ],
    }

    merged_tree = node_service.merge_nary_trees(tree1, tree2)
    assert len(merged_tree["children"]) == 1
    assert merged_tree["children"][0]["name"] == "child1"
    assert merged_tree["children"][0]["id"] == 2  # Prioridad al hijo del árbol 1


def test_merge_tree_with_none(node_service):
    tree1 = {
        "id": 1,
        "name": "root",
        "path": "/root",
        "parent_id": None,
        "single_child": False,
        "children": [],
    }
    tree2 = None

    merged_tree = node_service.merge_nary_trees(tree1, tree2)
    assert merged_tree == tree1


def test_merge_trees_with_single_child_attribute(node_service):
    tree1 = {
        "id": 1,
        "name": "root",
        "path": "/root",
        "parent_id": None,
        "single_child": True,
        "children": [
            {"id": 2, "name": "child1", "path": "/root/child1", "children": []}
        ],
    }
    tree2 = {
        "id": 1,
        "name": "root",
        "path": "/root",
        "parent_id": None,
        "single_child": True,
        "children": [
            {"id": 3, "name": "child2", "path": "/root/child2", "children": []}
        ],
    }

    merged_tree = node_service.merge_nary_trees(tree1, tree2)
    assert len(merged_tree["children"]) == 1
    assert (
        merged_tree["children"][0]["name"] == "child1"
    )  # Solo hijos de tree1 se mantienen


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


def test_find_child_with_name_direct_match(node_service):
    tree = {
        "name": "root",
        "children": [
            {"name": "child1", "children": []},
            {"name": "child2", "children": []},
        ],
    }
    assert node_service.find_child_with_name(tree, "child1") is True
    assert node_service.find_child_with_name(tree, "child2") is True


def test_find_child_with_name_nested_match(node_service):
    tree = {
        "name": "root",
        "children": [
            {
                "name": "child1",
                "children": [{"name": "grandchild1", "children": []}],
            },
            {"name": "child2", "children": []},
        ],
    }
    assert node_service.find_child_with_name(tree, "grandchild1") is True
    assert node_service.find_child_with_name(tree, "child2") is True


def test_find_child_with_name_no_match(node_service):
    tree = {
        "name": "root",
        "children": [
            {"name": "child1", "children": []},
            {"name": "child2", "children": []},
        ],
    }
    assert node_service.find_child_with_name(tree, "nonexistent") is False


def test_find_child_with_name_empty_tree(node_service):
    tree = {
        "name": "root",
        "children": [],
    }
    assert node_service.find_child_with_name(tree, "anyname") is False


def test_find_child_with_name_complex_tree(node_service):
    tree = {
        "name": "root",
        "children": [
            {
                "name": "child1",
                "children": [
                    {
                        "name": "grandchild1",
                        "children": [{"name": "greatgrandchild1", "children": []}],
                    },
                ],
            },
            {
                "name": "child2",
                "children": [
                    {"name": "grandchild2", "children": []},
                    {"name": "grandchild3", "children": []},
                ],
            },
        ],
    }
    assert node_service.find_child_with_name(tree, "greatgrandchild1") is True
    assert node_service.find_child_with_name(tree, "grandchild2") is True
    assert node_service.find_child_with_name(tree, "child1") is True
    assert node_service.find_child_with_name(tree, "nonexistent") is False


def test_merge_node_with_different_scenarios(node_service):
    """Prueba `merge_node` con diferentes escenarios."""
    app = create_app()

    # Datos iniciales y simulados
    node_id = 1
    user_id = 123

    # Nodo de ejemplo
    mock_node_data = {"id": node_id, "name": "0"}
    mock_tree_nodes_by_user = [
        {
            "id": node_id,
            "name": "0",
            "path": "3/7928339725:AAE6JYpPcd7x668IcIxIrlxwHB0Tx6DcqPI/4/1959498857/0",
            "single_child": 0,
            "children": [
                {
                    "name": "8",
                    "path": "3/7928339725:AAE6JYpPcd7x668IcIxIrlxwHB0Tx6DcqPI/4/1959498857/0/8",
                    "children": [
                        {
                            "name": "feature1",
                            "path": "3/7928339725:AAE6JYpPcd7x668IcIxIrlxwHB0Tx6DcqPI/4/1959498857/0/8/feature1",
                        },
                    ],
                },
            ],
        }
    ]
    mock_tree_nodes_by_bot = [
        {
            "id": 2,
            "name": "3",
            "path": "3",
            "single_child": 0,
            "children": [
                {
                    "name": "7928339725:AAE6JYpPcd7x668IcIxIrlxwHB0Tx6DcqPI",
                    "path": "3/7928339725:AAE6JYpPcd7x668IcIxIrlxwHB0Tx6DcqPI",
                    "children": [],
                },
            ],
        }
    ]

    with patch.object(
        node_service.repository, "get_node_by_id", return_value=mock_node_data
    ) as mock_get_node_by_id, patch.object(
        node_service.repository,
        "get_tree_nodes_by_user",
        return_value=[MagicMock(to_dict=lambda: mock_tree_nodes_by_user[0])],
    ) as mock_get_tree_nodes_by_user, patch.object(
        node_service.repository,
        "get_tree_nodes_by_bot",
        return_value=[MagicMock(to_dict=lambda: mock_tree_nodes_by_bot[0])],
    ) as mock_get_tree_nodes_by_bot, patch.object(
        node_service.repository, "update_node_name"
    ) as mock_update_node_name:
        with app.app_context():
            # Act - Llamada al método a probar
            result, status_code = node_service.merge_node(node_id, user_id)

            # Debugging: Imprimir el resultado de la ejecución
            print(result)  # Para ver qué devuelve la función
            print(status_code)

            # Assert - Validar que el resultado es exitoso
            assert status_code == 200
            assert result["message"] == "Node merged successfully!"
            assert result["node_id"] == node_id

            # Validar interacciones con el repositorio y servicios
            mock_get_node_by_id.assert_called_once_with(node_id)
            mock_update_node_name.assert_called_once_with(node_id, "1")
            mock_get_tree_nodes_by_user.assert_called_once_with(user_id)
            mock_get_tree_nodes_by_bot.assert_called_once()


def test_merge_node_node_not_found(node_service):
    """Prueba cuando el nodo no existe."""
    app = create_app()

    node_id = 1
    user_id = 123

    with patch.object(
        node_service.repository, "get_node_by_id", return_value=None
    ) as mock_get_node_by_id:
        with app.app_context():
            result, status_code = node_service.merge_node(node_id, user_id)

            assert status_code == 404
            assert result["error"] == "Node not found"
            mock_get_node_by_id.assert_called_once_with(node_id)


def test_merge_node_unexpected_error(node_service):
    """Prueba cuando ocurre un error inesperado."""
    app = create_app()

    node_id = 1
    user_id = 123

    with patch.object(
        node_service.repository,
        "get_node_by_id",
        side_effect=Exception("Unexpected error"),
    ) as mock_get_node_by_id:
        with app.app_context():
            result, status_code = node_service.merge_node(node_id, user_id)

            assert status_code == 500
            assert "error" in result
            assert result["error"] == "Unexpected error"
            mock_get_node_by_id.assert_called_once_with(node_id)


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


# Pruebas para load_messages
def test_load_messages_success():
    mock_yaml_content = """
    messages:
      AUTH:
        message: "Hello, {name}!"
    """
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        service = FeatureService()
        result = service.load_messages("fake_path.yaml")
        assert "messages" in result
        assert "AUTH" in result["messages"]


def test_load_messages_file_not_found():
    service = FeatureService()
    with pytest.raises(FileNotFoundError):
        service.load_messages("nonexistent.yaml")


def test_load_messages_yaml_error():
    invalid_yaml_content = """
    messages:
      AUTH: {invalid_yaml
    """
    with patch("builtins.open", mock_open(read_data=invalid_yaml_content)):
        service = FeatureService()
        with pytest.raises(yaml.YAMLError):
            service.load_messages("fake_path.yaml")


# Pruebas para get_bot_token
@patch(
    "builtins.open",
    mock_open(
        read_data="""
bottokens:
  - name: "@testbot"
    token: TEST_TOKEN_VAR
"""
    ),
)
@patch.dict(os.environ, {"TEST_TOKEN_VAR": "test_token_value"})
def test_get_bot_token_success():
    service = FeatureService()
    token = service.get_bot_token("@testbot", "fake_bottokens.yaml")
    assert token == "test_token_value"


@patch(
    "builtins.open",
    mock_open(
        read_data="""
bottokens:
  - name: "@testbot"
    token: TEST_TOKEN_VAR
"""
    ),
)
def test_get_bot_token_env_missing():
    service = FeatureService()
    with pytest.raises(ValueError):
        service.get_bot_token("@testbot", "fake_bottokens.yaml")


@patch(
    "builtins.open",
    mock_open(
        read_data="""
bottokens: []
"""
    ),
)
def test_get_bot_token_bot_not_found():
    service = FeatureService()
    with pytest.raises(ValueError):
        service.get_bot_token("@nonexistent_bot", "fake_bottokens.yaml")


@patch("app.modules.botintegration.models.TreeNode")
@patch("app.modules.auth.models.User")
@patch("app.modules.profile.models.UserProfile")
@patch("app.modules.botintegration.features.FeatureService.get_bot_token")
@patch("app.modules.botintegration.features.FeatureService.load_messages")
@patch("app.modules.botintegration.features.FeatureService.send_message_bot")
def test_send_features_bot(
    mock_send_message_bot,
    mock_load_messages,
    mock_get_bot_token,
    mock_user_profile,
    mock_user,
    mock_tree_node,
):
    # Setup del entorno
    app = create_app()
    with app.app_context():
        mock_get_bot_token.return_value = "test_token"
        mock_load_messages.return_value = {
            "messages": {"AUTH": {"message": "Hello, {name}!"}}
        }

        # Mock del modelo TreeNode
        mock_tree_node.query.filter.return_value.first.return_value = MagicMock(
            user_id=1, name="12345"
        )

        # Mock del modelo User
        mock_user.query.get.return_value = MagicMock(email="test@example.com")

        # Mock del modelo UserProfile
        user_profile_mock = MagicMock()
        user_profile_mock.name = (
            "Test"  # Aquí asignamos directamente el valor de 'name'
        )
        user_profile_mock.surname = "User"
        user_profile_mock.orcid = "0000-0000-0000-0000"

        # Establecemos que la consulta de UserProfile retorne este mock
        mock_user_profile.query.filter_by.return_value.first.return_value = (
            user_profile_mock
        )

        # Corre la función send_features_bot dentro del contexto de la aplicación

        service = FeatureService()
        service.send_features_bot(
            bot_token="@testbot",
            chat_id="12345",
            features=["AUTH"],
            BASE_URL="example.com",
        )

    # Verifica que se haya llamado a la función send_message_bot con los parámetros esperados
    mock_send_message_bot.assert_called_once()
    mock_send_message_bot.assert_called_with(
        "test_token", "12345", "AUTH", "Hello, Test!"  # El nombre debe ser "Test"
    )
