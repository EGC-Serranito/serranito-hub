from app.modules.botintegration.repositories import BotIntegrationRepository
from core.services.BaseService import BaseService


class NodeService(BaseService):
    """
    Service for managing tree nodes, including creating, updating, and deleting nodes.
    """

    def __init__(self):
        """
        Initializes the NodeService with the BotIntegrationRepository.
        """
        super().__init__(BotIntegrationRepository())

    def get_tree_nodes_by_user(self, user_id):
        """
        Retrieves tree nodes associated with a specific user.
        :param user_id: ID of the user
        :return: List of tree nodes
        """
        return self.repository.get_tree_nodes_by_user(user_id)

    def create_node_route_add_chat(self, user_id, name, parent_id, path, single_child):
        """
        Creates a node route for adding a chat.

        :param user_id: ID of the user
        :param name: Name of the node
        :param parent_id: ID of the parent node
        :param path: Path of the node
        :param single_child: Whether the node allows only a single child
        :return: Created node
        """
        return self.repository.create_node_route_add_chat(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )

    def create_node_route_add_bot(self, user_id, name, parent_id, path, single_child):
        """
        Creates a node route for adding a bot.

        :param user_id: ID of the user
        :param name: Name of the node
        :param parent_id: ID of the parent node
        :param path: Path of the node
        :param single_child: Whether the node allows only a single child
        :return: Created node
        """
        return self.repository.create_node_route_add_bot(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )

    def create_node_route_add_types_notification(self, user_id, name, parent_id, path, single_child):
        """
        Creates a node route for adding types of notifications.

        :param user_id: ID of the user
        :param name: Name of the node
        :param parent_id: ID of the parent node
        :param path: Path of the node
        :param single_child: Whether the node allows only a single child
        :return: Created node
        """
        return self.repository.create_node_route_add_types_notification(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )

    def create_node_route_add_feature(self, user_id, name, parent_id, path, single_child):
        """
        Creates a node route for adding a feature.

        :param user_id: ID of the user
        :param name: Name of the node
        :param parent_id: ID of the parent node
        :param path: Path of the node
        :param single_child: Whether the node allows only a single child
        :return: Created node
        """
        return self.repository.create_node_route_add_feature(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )

    def delete_node(self, node_id):
        """
        Deletes a node by its ID.

        :param node_id: ID of the node to be deleted
        :return: Result of the deletion operation
        """
        return self.repository.delete_node(node_id)
