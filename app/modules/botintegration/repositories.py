from app import db
from app.modules.botintegration.models import TreeNode
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

            # Agregar más nodos hijos en cadena
            path_child = f"{path_child}/NOTIFICATION PREFERENCE"
            notification_node = TreeNode(
                user_id=user_id,
                name="NOTIFICATION PREFERENCE",
                parent_id=child_one_node.id,
                path=path_child,
                single_child=single_child
            )
            db.session.add(notification_node)
            db.session.commit()

            # Continuar agregando más nodos hijos en la jerarquía
            path_child = f"{path_child}/TYPES OF NOTIFICATION"
            types_node = TreeNode(
                user_id=user_id,
                name="TYPES OF NOTIFICATION",
                parent_id=notification_node.id,
                path=path_child,
                single_child=single_child
            )
            db.session.add(types_node)
            db.session.commit()

            path_child = f"{path_child}/NEW MESSAGES"
            new_messages_node = TreeNode(
                user_id=user_id,
                name="NEW MESSAGES",
                parent_id=types_node.id,
                path=path_child,
                single_child=single_child
            )
            db.session.add(new_messages_node)
            db.session.commit()

            path_child = f"{path_child}/IMMEDIATELY"
            immediately_node = TreeNode(
                user_id=user_id,
                name="IMMEDIATELY",
                parent_id=new_messages_node.id,
                path=path_child,
                single_child=single_child
            )
            db.session.add(immediately_node)
            db.session.commit()

            path_child = f"{path_child}/SYSTEM ERRORS"
            system_errors_node = TreeNode(
                user_id=user_id,
                name="SYSTEM ERRORS",
                parent_id=types_node.id,
                path=path_child,
                single_child=single_child
            )
            db.session.add(system_errors_node)
            db.session.commit()

            path_child = f"{path_child}/IMMEDIATELY"
            system_immediately_node = TreeNode(
                user_id=user_id,
                name="IMMEDIATELY",
                parent_id=system_errors_node.id,
                path=path_child,
                single_child=single_child
            )
            db.session.add(system_immediately_node)
            db.session.commit()

            path_child = f"{path_child}/FEATURES"
            features_node = TreeNode(
                user_id=user_id,
                name="FEATURES",
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
                    name="TELEGRAM BOTS",
                    parent_id=None,
                    path=path,
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

                chat_path = f"{bot_path}/CHATS"
                child_one_node = TreeNode(
                    user_id=user_id,
                    name="CHATS",
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

                chat_path = f"{path}/CHATS"
                child_one_node = TreeNode(
                    user_id=user_id,
                    name="CHATS",
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
        Elimina un nodo, sus descendientes y sus registros asociados en TreeNodeBot.

        :param node_id: ID del nodo a eliminar.
        :return: True si se eliminó correctamente, False en caso de error.
        """
        try:
            db.session.query(TreeNode).filter(TreeNode.id == node_id).delete()
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error deleting node: {e}")
            return False
