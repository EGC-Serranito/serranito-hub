from app.modules.botintegration.repositories import BotIntegrationRepository
from core.services.BaseService import BaseService
from app.modules.botintegration.features import FeatureService
import os

featureService = FeatureService()


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
        return self.repository.get_tree_nodes_by_user(user_id)

    def get_tree_nodes_by_path(self, node_path):
        return self.get_tree_nodes_by_path(node_path)

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
        print(self.repository.get_children_count(parent_id))
        if self.repository.get_children_count(parent_id) <= 2:
            return self.repository.create_node_route_add_chat(
                user_id=user_id,
                name=name,
                parent_id=parent_id,
                path=path,
                single_child=single_child,
            )
        else:
            return {"error": "A bot can be configured with a maximum of 3 chats at a time."}, 400

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
        print(self.repository.get_children_count(parent_id))
        if self.repository.get_children_count(parent_id) <= 4:
            return self.repository.create_node_route_add_bot(
                user_id=user_id,
                name=name,
                parent_id=parent_id,
                path=path,
                single_child=single_child,
            )
        else:
            return {"error": "A maximum of 5 bots can be configured."}, 400

    def create_node_route_add_types_notification(
        self, user_id, name, parent_id, path, single_child
    ):
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
            single_child=single_child,
        )

    def create_node_route_add_feature(
        self, user_id, name, parent_id, path, single_child
    ):
        """
        Creates a node route for adding a feature.

        :param user_id: ID of the user
        :param name: Name of the node
        :param parent_id: ID of the parent node
        :param path: Path of the node
        :param single_child: Whether the node allows only a single child
        :return: Created node
        """
        if self.repository.get_children_count(parent_id) <= 2:
            return self.repository.create_node_route_add_feature(
                user_id=user_id,
                name=name,
                parent_id=parent_id,
                path=path,
                single_child=single_child,
            )
        else:
            return {"error": "A bot can be configured with a maximum of 3 features at a time."}, 400

    def delete_node(self, node_id):
        """
        Deletes a node by its ID.

        :param node_id: ID of the node to be deleted
        :return: Result of the deletion operation
        """
        return self.repository.delete_node(node_id)

    def find_child_with_name(self, child, name_to_find):
        """Función recursiva para encontrar un nodo con un nombre específico en los hijos."""
        if child.get("name") == name_to_find:
            return True
        for grandchild in child.get("children", []):
            if self.find_child_with_name(grandchild, name_to_find):
                return True
        return False

    def merge_node(self, node_id, user_id):
        try:
            node_data = self.repository.get_node_by_id(node_id)
            if not node_data:
                return {"error": "Node not found"}, 404

            current_name = node_data["name"]
            new_name = (
                "0"
                if current_name == "1"
                else "1" if current_name == "0" else current_name
            )
            self.repository.update_node_name(node_id, new_name)

            treenode_bot = self.repository.get_tree_nodes_by_bot()
            tree_nodes = self.repository.get_tree_nodes_by_user(user_id)
            tree_nodes_dict = (
                [node.to_dict() for node in tree_nodes] if tree_nodes else []
            )
            treenode_bot_dict = (
                [node.to_dict() for node in treenode_bot] if treenode_bot else []
            )

            for node in tree_nodes_dict:
                if node_data["name"] == "0" and node.get("id") == node_id:
                    if self.find_child_with_name(node, "7"):
                        if len(node.get("children", [])) > 1:
                            second_child = node.get("children")[1]
                            BOT_TOKEN = second_child.get("path").split("/")[1]
                            CHAT_ID = second_child.get("path").split("/")[3]
                            features = [
                                feature.get("name")
                                for feature in second_child.get("children", [])
                            ]
                            if features:
                                featureService.send_features_bot(
                                    BOT_TOKEN,
                                    CHAT_ID,
                                    features,
                                    featureService.transform_to_full_url(
                                        os.getenv("DOMAIN", "localhost")
                                    ),
                                )
                                print(features)
                                print(BOT_TOKEN)
                                print(CHAT_ID)
                                node_data = self.repository.get_node_by_id(node_id)
                                if not node_data:
                                    return {"error": "Node not found"}, 404

                                current_name = node_data["name"]
                                new_name = (
                                    "0"
                                    if current_name == "1"
                                    else "1" if current_name == "0" else current_name
                                )
                                self.repository.update_node_name(node_id, new_name)
                            else:
                                return {"error": "No features found in the children of the second child."}, 400
                        else:
                            return {"error": "The node does not have a second child."}, 400
                    else:
                        if len(node.get("children", [])) > 1:
                            second_child = node.get("children")[1]
                            BOT_TOKEN = second_child.get("path").split("/")[1]
                            CHAT_ID = second_child.get("path").split("/")[3]
                            features = [
                                feature.get("name")
                                for feature in second_child.get("children", [])
                            ]
                            if features:
                                featureService.send_features_bot(
                                    BOT_TOKEN,
                                    CHAT_ID,
                                    features,
                                    featureService.transform_to_full_url(
                                        os.getenv("DOMAIN", "localhost")
                                    ),
                                )

                                if not tree_nodes_dict:
                                    return {"error": "User tree is empty"}, 400

                                if treenode_bot_dict:
                                    self.remove_stopped_chats(treenode_bot_dict[0])
                                    merged_tree = self.merge_nary_trees(
                                        tree_nodes_dict[0], treenode_bot_dict[0]
                                    )
                                else:
                                    merged_tree = tree_nodes_dict[0]

                                if not merged_tree or "name" not in merged_tree:
                                    raise ValueError("Merged tree is invalid.")

                                self.remove_stopped_chats(merged_tree)

                                def print_tree(node, level=0):
                                    print("\t" * level + f"- {node['name']} ----- {node['path']}")
                                    for child in node.get("children", []):
                                        print_tree(child, level + 1)

                                print_tree(merged_tree)

                                self.repository.clear_treenode_bot_table()
                                self.repository.save_bot_tree_to_db(merged_tree)
                            else:
                                return {"error": "No features found in the children of the second child."}, 400
                        else:
                            return {"error": "The node does not have a second child."}, 400
            return {"message": "Chat run successfully!", "node_id": node_id}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def merge_nary_trees(self, tree1, tree2):
        """
        Combina dos árboles n-arios representados como diccionarios.
        Si un nodo existe en ambos árboles (basado en el atributo 'name'), sus hijos se fusionan.
        Si solo existe en uno, se agrega directamente.

        :param tree1: Diccionario que representa el primer árbol.
        :param tree2: Diccionario que representa el segundo árbol.
        :return: Diccionario que representa el árbol fusionado.
        """
        if not tree1:
            return tree2
        if not tree2:
            return tree1

        merged_node = {
            "id": tree1.get("id") or tree2.get("id"),
            "name": tree1["name"],
            "path": tree1["path"],
            "parent_id": tree1.get("parent_id") or tree2.get("parent_id"),
            "single_child": tree1.get("single_child") or tree2.get("single_child"),
            "children": [],
        }

        children_map = {child["name"]: child for child in tree1.get("children", [])}

        for child2 in tree2.get("children", []):
            if child2["name"] in children_map:
                merged_child = self.merge_nary_trees(
                    children_map[child2["name"]], child2
                )
                merged_node["children"].append(merged_child)
                del children_map[child2["name"]]
            else:
                if not tree2.get("single_child", False):
                    merged_node["children"].append(child2)

        merged_node["children"].extend(children_map.values())

        return merged_node

    def remove_stopped_chats(self, node):
        """
        Removes chat nodes that have a state "0" under nodes '4',
        or nodes with state "1" that have children with name "7".

        :param node: Node of the tree to process.
        """
        for child in node.get("children", []):
            if child["name"] == "4":
                child["children"] = [
                    chat
                    for chat in child.get("children", [])
                    if not (
                        any(
                            grandchild["name"] == "0"
                            for grandchild in chat.get("children", [])
                        )
                        or (
                            chat["name"] == "1"
                            and any(
                                grandchild["name"] == "7"
                                for grandchild in chat.get("children", [])
                            )
                        )
                    )
                ]
            else:
                self.remove_stopped_chats(child)
