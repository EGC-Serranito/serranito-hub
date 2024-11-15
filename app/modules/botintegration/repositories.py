from app import db
from app.modules.botintegration.models import TreeNode, TreeNodeBot
from core.repositories.BaseRepository import BaseRepository
from sqlalchemy.exc import SQLAlchemyError


class BotIntegrationRepository(BaseRepository):
    def __init__(self):
        super().__init__(TreeNode)

    def get_tree_nodes_by_user(self, user_id):
        """
        Obtiene todos los nodos del árbol (TreeNode) asociados a un usuario específico.

        :param user_id: ID del usuario logueado.
        :return: Una lista de nodos (TreeNode) asociados a este usuario.
        """
        try:
            nodes = (
                db.session.query(TreeNode)
                .filter(TreeNode.user_id == user_id)
                .all()
            )
            return nodes
        except Exception as e:
            db.session.rollback()
            raise e

    def get_tree_nodes_by_bot(self):
        """
        Obtiene todos los nodos del árbol (TreeNodeBot).
        :return: Una lista de nodos (TreeNodeBot).
        """
        try:
            nodes = db.session.query(TreeNodeBot).all()
            return nodes
        except Exception as e:
            db.session.rollback()
            raise e

    def clear_treenode_bot_table(self):
        """
        Limpia la tabla `treenode_bot` eliminando todos los registros.

        :return: None
        """
        try:
            db.session.query(TreeNodeBot).delete()  # Eliminar todos los registros de la tabla TreeNodeBot
            db.session.commit()  # Confirmar los cambios
        except SQLAlchemyError as e:
            db.session.rollback()  # Revertir los cambios en caso de error
            raise e

    def save_bot_tree_to_db(self, root_node):
        """
        Guarda un árbol combinado en la tabla `treenode_bot`.

        :param root_node: Nodo raíz del árbol a guardar.
        """
        try:
            def save_node(node, parent_id=None, parent_path=""):
                """
                Función recursiva para guardar un nodo y sus hijos en la base de datos.

                :param node: Nodo a guardar.
                :param parent_id: ID del nodo padre en la base de datos.
                :param parent_path: Ruta del nodo padre.
                """
                # Generar el path para el nodo actual
                node["path"] = f"{parent_path}/{node['name']}".strip("/")

                # Crear un nuevo nodo en la base de datos
                new_node = TreeNodeBot(
                    name=node["name"],
                    parent_id=parent_id,
                    path=node["path"],  # Ahora el path está asegurado
                    single_child=node.get("single_child", False)  # Valor por defecto es False si no se proporciona.
                )

                # Añadir el nodo a la sesión
                db.session.add(new_node)
                db.session.commit()  # Commit para obtener el ID generado para este nodo

                # Recursivamente guardar los hijos del nodo actual
                for child in node.get("children", []):
                    save_node(child, new_node.id, node["path"])

            # Comienza guardando el árbol desde el nodo raíz
            save_node(root_node)
            db.session.commit()  # Confirmar todos los cambios realizados
        except SQLAlchemyError:
            db.session.rollback()  # Revertir los cambios en caso de error
            # Devolver un mensaje controlado de error sin imprimirlo
            return {"error": "Error al guardar el árbol en la base de datos. Intente nuevamente."}, 500

    def create_node_route_add_chat(self, user_id, name, parent_id, path, single_child):
        try:
            # Crear el nodo principal
            new_node = TreeNode(
                user_id=user_id,
                name=name,
                parent_id=parent_id,
                path=path,
                single_child=single_child
            )
            db.session.add(new_node)
            db.session.commit()

            # Crear nodos hijos
            path_child = f"{path}/0"
            child_one_node = TreeNode(
                user_id=user_id,
                name="0",
                parent_id=new_node.id,
                path=path_child,
                single_child=single_child
            )
            db.session.add(child_one_node)
            db.session.commit()

            # Continuar agregando más nodos hijos en la jerarquía
            path_child = f"{path_child}/5"
            types_node = TreeNode(
                user_id=user_id,
                name="5",
                parent_id=child_one_node.id,
                path=path_child,
                single_child=single_child
            )
            db.session.add(types_node)
            db.session.commit()

            path_child = f"{path_child}/6"
            new_messages_node = TreeNode(
                user_id=user_id,
                name="6",
                parent_id=types_node.id,
                path=path_child,
                single_child=True
            )
            db.session.add(new_messages_node)
            db.session.commit()

            path_child = f"{path_child}/7"
            immediately_node = TreeNode(
                user_id=user_id,
                name="7",
                parent_id=new_messages_node.id,
                path=path_child,
                single_child=True
            )
            db.session.add(immediately_node)
            db.session.commit()

            path_child = f"{path_child}/8"
            features_node = TreeNode(
                user_id=user_id,
                name="8",
                parent_id=child_one_node.id,
                path=path_child,
                single_child=single_child
            )
            db.session.add(features_node)
            db.session.commit()

            return new_node

        except Exception as e:
            db.session.rollback()
            raise e

    def create_node_route_add_bot(self, user_id, name, parent_id, path, single_child):
        try:
            if not parent_id:
                new_node = TreeNode(
                    user_id=user_id,
                    name="3",
                    parent_id=None,
                    path="3",
                    single_child=single_child
                )
                db.session.add(new_node)
                db.session.commit()

                bot_path = f"{path}/{name}"
                child_bot_node = TreeNode(
                    user_id=user_id,
                    name=name,
                    parent_id=new_node.id,
                    path=bot_path,
                    single_child=single_child
                )
                db.session.add(child_bot_node)
                db.session.commit()

                chat_path = f"{bot_path}/4"
                child_one_node = TreeNode(
                    user_id=user_id,
                    name="4",
                    parent_id=child_bot_node.id,
                    path=chat_path,
                    single_child=single_child
                )
                db.session.add(child_one_node)
                db.session.commit()
            else:
                new_node = TreeNode(
                    user_id=user_id,
                    name=name,
                    parent_id=parent_id,
                    path=path,
                    single_child=single_child
                )
                db.session.add(new_node)
                db.session.commit()

                chat_path = f"{path}/4"
                child_one_node = TreeNode(
                    user_id=user_id,
                    name="4",
                    parent_id=new_node.id,
                    path=chat_path,
                    single_child=single_child
                )
                db.session.add(child_one_node)
                db.session.commit()

            return new_node
        except Exception as e:
            db.session.rollback()
            raise e

    def create_node_route_add_feature(self, user_id, name, parent_id, path, single_child):
        try:
            new_node = TreeNode(
                user_id=user_id,
                name=name,
                parent_id=parent_id,
                path=path,
                single_child=single_child
            )
            db.session.add(new_node)
            db.session.commit()
            return new_node
        except Exception as e:
            db.session.rollback()
            raise e

    def create_node_route_add_types_notification(self, user_id, name, parent_id, path, single_child):
        try:
            db.session.query(TreeNode).filter(
                TreeNode.parent_id == parent_id
            ).delete()
            db.session.commit()

            new_node = TreeNode(
                user_id=user_id,
                name=name,
                parent_id=parent_id,
                path=path,
                single_child=single_child
            )
            db.session.add(new_node)
            db.session.commit()
            return new_node
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_node(self, node_id):
        """
        Elimina un nodo, sus descendientes y sus registros asociados en TreeNodeBot basados en el path del nodo.

        :param node_id: ID del nodo a eliminar.
        :return: True si se eliminó correctamente, False en caso de error.
        """
        try:
            # Recuperar el nodo con el node_id
            node_to_delete = db.session.query(TreeNode).filter(TreeNode.id == node_id).first()

            if node_to_delete:
                # Obtener el path del nodo
                node_path = node_to_delete.path

                # Eliminar los registros en TreeNodeBot con el mismo path
                db.session.query(TreeNodeBot).filter(TreeNodeBot.path == node_path).delete()

                # Eliminar el nodo de la tabla TreeNode
                db.session.query(TreeNode).filter(TreeNode.id == node_id).delete()

                # Confirmar cambios
                db.session.commit()
                return True
            else:
                # Si no se encuentra el nodo
                print(f"Node with ID {node_id} not found.")
                return False

        except SQLAlchemyError as e:
            # Si hay algún error, revertimos la transacción
            db.session.rollback()
            print(f"Error deleting node: {e}")
            return False

    def get_node_by_id(self, node_id):
        """
        Obtiene un nodo por su ID.

        :param node_id: ID del nodo.
        :return: Diccionario con los datos del nodo o None si no se encuentra.
        """
        try:
            node = db.session.query(TreeNode).filter(TreeNode.id == node_id).one_or_none()
            if node:
                return {
                    "id": node.id,
                    "name": node.name,
                    "parent_id": node.parent_id,
                    "path": node.path,
                    "single_child": node.single_child
                }
            return None
        except Exception as exc:
            db.session.rollback()
            raise exc

    def update_node_name(self, node_id, new_name):
        """
        Actualiza el nombre de un nodo en la base de datos.

        :param node_id: ID del nodo.
        :param new_name: Nuevo nombre para el nodo.
        """
        try:
            db.session.query(TreeNode).filter(TreeNode.id == node_id).update({"name": new_name})
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise exc
