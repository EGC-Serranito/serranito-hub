import pytest
from unittest.mock import MagicMock, patch
from app.modules.auth.models import User
from app.modules.botintegration.services import NodeService
from app import create_app


@pytest.fixture
def node_service():
    """Fixture para el servicio NodeService."""
    return NodeService()


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
    app = create_app()
    with app.app_context():
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
    app = create_app()
    with app.app_context():
        tree_node_bot = MagicMock()
        tree_node_bot.id = 2
        tree_node_bot.name = "@uvlhub_telegram1"
        tree_node_bot.path = "3/@uvlhub_telegram1"
        tree_node_bot.single_child = True
        tree_node_bot.children = []
        return tree_node_bot


def test_create_node_route_add_chat_success(node_service, mock_user):
    """Test creating a chat node successfully when there are fewer than 3 children."""
    app = create_app()
    with app.app_context():
        with patch.object(node_service.repository, "get_children_count", return_value=2), \
            patch.object(node_service.repository, "create_node_route_add_chat",
                         return_value={"status": "success"}) as mock_create_node:
            result = node_service.create_node_route_add_chat(
                user_id=mock_user.id,
                name="Chat1",
                parent_id=1,
                path="path/to/chat",
                single_child=False
            )

            mock_create_node.assert_called_once_with(
                user_id=mock_user.id,
                name="Chat1",
                parent_id=1,
                path="path/to/chat",
                single_child=False
            )
            assert result["status"] == "success"


def test_create_node_route_add_chat_limit_exceeded(node_service, mock_user):
    """Test the error response when the bot has 3 or more chats."""
    app = create_app()
    with app.app_context():
        with patch.object(node_service.repository, "get_children_count", return_value=3):
            result = node_service.create_node_route_add_chat(
                user_id=mock_user.id,
                name="Chat4",
                parent_id=1,
                path="path/to/chat",
                single_child=False
            )

            assert result[1] == 400


def test_create_node_route_add_bot_success(node_service, mock_user):
    """Test creating a bot node successfully when there are fewer than 5 children."""
    app = create_app()
    with app.app_context():
        with patch.object(node_service.repository, "get_children_count", return_value=4), \
            patch.object(node_service.repository, "create_node_route_add_bot",
                         return_value={"status": "success"}) as mock_create_node:

            result = node_service.create_node_route_add_bot(
                user_id=mock_user.id,
                name="Bot1",
                parent_id=1,
                path="path/to/bot",
                single_child=False
            )

            # Check that the bot creation method was called
            mock_create_node.assert_called_once_with(
                user_id=mock_user.id,
                name="Bot1",
                parent_id=1,
                path="path/to/bot",
                single_child=False
            )
            assert result["status"] == "success"


def test_create_node_route_add_bot_limit_exceeded(node_service, mock_user):
    """Test the error response when the bot has 5 or more bots."""
    app = create_app()
    with app.app_context():
        with patch.object(node_service.repository, "get_children_count", return_value=5):
            result = node_service.create_node_route_add_bot(
                user_id=mock_user.id,
                name="Bot6",
                parent_id=1,
                path="path/to/bot",
                single_child=False
            )
            assert result[1] == 400


def test_create_node_route_add_types_notification(node_service, mock_user):
    """Test creating a types notification node."""
    app = create_app()
    with app.app_context():
        with patch.object(node_service.repository, "create_node_route_add_types_notification",
                          return_value={"status": "success"}) as mock_create_node:

            result = node_service.create_node_route_add_types_notification(
                user_id=mock_user.id,
                name="NotificationType1",
                parent_id=1,
                path="path/to/notification",
                single_child=False
            )

            mock_create_node.assert_called_once_with(
                user_id=mock_user.id,
                name="NotificationType1",
                parent_id=1,
                path="path/to/notification",
                single_child=False
            )
            assert result["status"] == "success"


def test_delete_node(node_service):
    """Prueba la eliminación de un nodo por su ID."""
    app = create_app()
    with app.app_context():
        with patch.object(
            node_service.repository,
            "delete_node",
            return_value={"status": "success", "message": "Node deleted"},
        ) as mock_delete_node:
            result = node_service.delete_node(node_id=1)

            assert result["status"] == "success"
            assert result["message"] == "Node deleted"

            mock_delete_node.assert_called_once_with(1)


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
                    {"name": "1", "children": [{"name": "7"}]},
                    {"name": "1", "children": []},
                    {"name": "0", "children": []},
                ],
            }
        ],
    }

    node_service.remove_stopped_chats(tree)

    assert len(tree["children"][0]["children"]) == 2
    assert tree["children"][0]["children"][0]["name"] == "1"
    assert not tree["children"][0]["children"][0]["children"]
