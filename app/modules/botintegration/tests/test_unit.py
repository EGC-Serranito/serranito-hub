import pytest
from unittest.mock import MagicMock, mock_open, patch
from app.modules.botintegration.features import FeatureService
from app.modules.botintegration.services import NodeService
from app import create_app
import os


@pytest.fixture
def app_context():
    """Fixture para crear un contexto de aplicación."""
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture
def node_service():
    """Fixture para el servicio NodeService."""
    return NodeService()


@pytest.fixture
def feature_service():
    """Fixture para el servicio NodeService."""
    return FeatureService()


@pytest.fixture
def mock_treenode():
    """
    Fixture para un TreeNode simulado basado en `mock_tree_nodes_by_user`.
    """
    tree_node = MagicMock()
    tree_node.id = 1
    tree_node.name = "0"
    tree_node.user_id = 1
    tree_node.path = "3/@uvlhub_telegram1/4/1959498857/0"
    tree_node.single_child = False
    tree_node.children = [
        MagicMock(
            name="8",
            path="3/@uvlhub_telegram1/4/1959498857/0/8",
            children=[
                MagicMock(
                    name="AUTH",
                    path="3/@uvlhub_telegram1/4/1959498857/0/8/AUTH",
                    children=[],
                )
            ],
        )
    ]
    return tree_node


@pytest.fixture
def mock_treenode_bot():
    """
    Fixture para un TreeNodeBot simulado.
    """
    tree_node_bot = MagicMock()
    tree_node_bot.id = 2
    tree_node_bot.name = "@uvlhub_telegram1"
    tree_node_bot.path = "3/@uvlhub_telegram1"
    tree_node_bot.single_child = True
    tree_node_bot.children = []
    return tree_node_bot


def test_create_node_route_add_chat(node_service):
    """Prueba la creación de un nodo tipo chat."""
    with patch.object(
        node_service.repository,
        "create_node_route_add_chat",
        return_value={"id": 1, "name": "test_chat"},
    ) as mock_create_chat:
        result = node_service.create_node_route_add_chat(
            user_id=1,
            name="test_chat",
            parent_id=None,
            path="/test/chat",
            single_child=False,
        )
        assert result["id"] == 1
        assert result["name"] == "test_chat"
        mock_create_chat.assert_called_once_with(
            user_id=1,
            name="test_chat",
            parent_id=None,
            path="/test/chat",
            single_child=False,
        )


def test_find_child_with_name_found(node_service):
    """Prueba para encontrar un nodo hijo con un nombre específico."""
    tree = {
        "name": "root",
        "children": [
            {"name": "child1", "children": []},
            {"name": "child2", "children": []},
        ],
    }
    assert node_service.find_child_with_name(tree, "child1") is True


def test_find_child_with_name_not_found(node_service):
    """Prueba para buscar un nodo hijo con un nombre que no existe."""
    tree = {
        "name": "root",
        "children": [
            {"name": "child1", "children": []},
            {"name": "child2", "children": []},
        ],
    }
    assert node_service.find_child_with_name(tree, "nonexistent") is False


def test_merge_nary_trees(node_service):
    """Prueba la fusión de dos árboles."""
    tree1 = {
        "name": "root",
        "path": "root",
        "children": [{"name": "child1", "children": []}],
    }
    tree2 = {
        "name": "root",
        "path": "root",
        "children": [{"name": "child2", "children": []}],
    }
    merged_tree = node_service.merge_nary_trees(tree1, tree2)
    assert len(merged_tree["children"]) == 2
    assert any(child["name"] == "child1" for child in merged_tree["children"])
    assert any(child["name"] == "child2" for child in merged_tree["children"])


def test_merge_trees_with_mock_data(node_service, mock_treenode, mock_treenode_bot):
    """
    Prueba la fusión de árboles usando mock_treenode y mock_treenode_bot.
    """
    tree_user = {
        "id": mock_treenode.id,
        "name": mock_treenode.name,
        "path": mock_treenode.path,
        "single_child": mock_treenode.single_child,
        "children": [
            {
                "name": mock_treenode.children[0].name,
                "path": mock_treenode.children[0].path,
                "children": [
                    {
                        "name": mock_treenode.children[0].children[0].name,
                        "path": mock_treenode.children[0].children[0].path,
                        "children": [],
                    }
                ],
            }
        ],
    }

    tree_bot = {
        "id": mock_treenode_bot.id,
        "name": mock_treenode_bot.name,
        "path": mock_treenode_bot.path,
        "single_child": mock_treenode_bot.single_child,
        "children": [],
    }

    merged_tree = node_service.merge_nary_trees(tree_user, tree_bot)

    assert merged_tree["name"] == "0"
    assert len(merged_tree["children"]) == 1


def test_remove_stopped_chats_with_mock_data(node_service, mock_treenode):
    """
    Prueba la eliminación de chats detenidos usando mock_treenode.
    """
    tree = {
        "id": mock_treenode.id,
        "name": mock_treenode.name,
        "path": mock_treenode.path,
        "single_child": mock_treenode.single_child,
        "children": [
            {
                "name": "4",
                "children": [
                    {"name": "1", "children": [{"name": "7"}]},  # Nodo a eliminar
                    {"name": "1", "children": []},  # Nodo que permanece
                    {"name": "0", "children": []},  # Nodo a eliminar
                ],
            }
        ],
    }

    node_service.remove_stopped_chats(tree)

    assert len(tree["children"][0]["children"]) == 2
    assert tree["children"][0]["children"][0]["name"] == "1"
    assert not tree["children"][0]["children"][0]["children"]


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
def test_get_bot_token_success(feature_service):
    token = feature_service.get_bot_token("@testbot", "fake_bottokens.yaml")
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
def test_get_bot_token_env_missing(feature_service):
    with pytest.raises(ValueError):
        feature_service.get_bot_token("@testbot", "fake_bottokens.yaml")


@patch(
    "builtins.open",
    mock_open(
        read_data="""
bottokens: []
"""
    ),
)
def test_get_bot_token_bot_not_found(feature_service):
    with pytest.raises(ValueError):
        feature_service.get_bot_token("@nonexistent_bot", "fake_bottokens.yaml")


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
    feature_service
):

    app = create_app()
    with app.app_context():
        mock_get_bot_token.return_value = "test_token"
        mock_load_messages.return_value = {
            "messages": {"AUTH": {"message": "Hello, {name}!"}}
        }

        mock_tree_node.query.filter.return_value.first.return_value = MagicMock(
            user_id=1, name="12345"
        )

        mock_user.query.get.return_value = MagicMock(email="test@example.com")

        user_profile_mock = MagicMock()
        user_profile_mock.name = "Test"
        user_profile_mock.surname = "User"
        user_profile_mock.orcid = "0000-0000-0000-0000"

        mock_user_profile.query.filter_by.return_value.first.return_value = (
            user_profile_mock
        )

        feature_service.send_features_bot(
            bot_token="@testbot",
            chat_id="12345",
            features=["AUTH"],
            BASE_URL="example.com",
        )

    mock_send_message_bot.assert_called_once()
    mock_send_message_bot.assert_called_with(
        "test_token", "12345", "AUTH", "Hello, Test!"
    )
