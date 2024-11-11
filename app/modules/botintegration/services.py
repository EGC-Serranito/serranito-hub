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
            single_child=single_child,
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
            single_child=single_child,
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
            single_child=single_child,
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
            single_child=single_child,
        )

    def delete_node(self, node_id):
        """
        Deletes a node by its ID.

        :param node_id: ID of the node to be deleted
        :return: Result of the deletion operation
        """
        return self.repository.delete_node(node_id)

    def merge_node(self, node_id, user_id):
        try:
            # Recuperar datos del nodo
            node_data = self.repository.get_node_by_id(node_id)
            if not node_data:
                return {"error": "Node not found"}, 404

            current_name = node_data["name"]
            new_name = "0" if current_name == "1" else "1" if current_name == "0" else current_name
            self.repository.update_node_name(node_id, new_name)

            # Recuperar árboles
            treenode_bot = self.repository.get_tree_nodes_by_bot()
            tree_nodes = self.repository.get_tree_nodes_by_user(user_id)
            tree_nodes_dict = [node.to_dict() for node in tree_nodes] if tree_nodes else []
            treenode_bot_dict = [node.to_dict() for node in treenode_bot] if treenode_bot else []

            if not tree_nodes_dict:
                return {"error": "User tree is empty"}, 400

            # Limpieza y fusión de árboles
            if treenode_bot_dict:
                self.remove_stopped_chats(treenode_bot_dict[0])
                merged_tree = self.merge_nary_trees(tree_nodes_dict[0], treenode_bot_dict[0])
            else:
                merged_tree = tree_nodes_dict[0]

            # Validación y limpieza final
            if not merged_tree or "name" not in merged_tree:
                raise ValueError("Merged tree is invalid.")

            self.remove_stopped_chats(merged_tree)

            # Visualización del árbol
            def print_tree(node, level=0):
                print("\t" * level + f"- {node['name']}")
                for child in node.get("children", []):
                    print_tree(child, level + 1)

            print_tree(merged_tree)

            # Guardar árbol combinado en la base de datos
            self.repository.clear_treenode_bot_table()
            self.repository.save_bot_tree_to_db(merged_tree)

            return {"message": "Node merged successfully!", "node_id": node_id}, 200

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
        # Caso base: Si uno de los árboles es None, devolver el otro
        if not tree1:
            return tree2
        if not tree2:
            return tree1

        # Crear el nodo fusionado con la información del primer árbol (tree1)
        merged_node = {
            "id": tree1.get("id") or tree2.get("id"),
            "name": tree1["name"],  # Usamos el nombre del primer árbol
            "path": tree1["path"],  # Mantén el path del primer árbol
            "parent_id": tree1.get("parent_id") or tree2.get("parent_id"),
            "single_child": tree1.get("single_child") or tree2.get("single_child"),
            "children": []
        }

        # Crear un mapa para los hijos de tree1 usando el atributo 'name' como clave
        children_map = {child["name"]: child for child in tree1.get("children", [])}

        # Procesar los hijos de tree2
        for child2 in tree2.get("children", []):
            if child2["name"] in children_map:
                # Si el hijo existe en ambos árboles, fusiónalos recursivamente
                merged_child = self.merge_nary_trees(children_map[child2["name"]], child2)
                merged_node["children"].append(merged_child)
                del children_map[child2["name"]]  # Eliminar el hijo fusionado del mapa
            else:
                # Si no existe en tree1, verifica el atributo single_child antes de agregar
                if not tree2.get("single_child", False):
                    merged_node["children"].append(child2)

        # Agregar los hijos restantes de tree1 que no fueron fusionados
        merged_node["children"].extend(children_map.values())

        return merged_node

    def remove_stopped_chats(self, node):
        """
        Elimina los nodos de chat que tienen un estado "0" bajo nodos 'CHATS'.

        :param node: Nodo del árbol para procesar.
        """
        # Procesar los hijos del nodo actual
        for child in node.get("children", []):
            if child["name"] == "CHATS":
                # Filtrar los chats que no tienen hijos con nombre "0"
                child["children"] = [
                    chat for chat in child.get("children", [])
                    if not any(grandchild["name"] == "0" for grandchild in chat.get("children", []))
                ]
            else:
                # Llamada recursiva para los demás nodos
                self.remove_stopped_chats(child)
