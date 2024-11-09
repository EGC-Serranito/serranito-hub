from app.modules.botintegration.repositories import BotIntegrationRepository
from core.services.BaseService import BaseService


class NodeService(BaseService):
    def __init__(self):
        super().__init__(BotIntegrationRepository())

    def get_tree_nodes_by_user(self, user_id):
        return self.repository.get_tree_nodes_by_user(user_id)

    def create_node_route_add_chat(self, user_id, name, parent_id, path, single_child):
        return self.repository.create_node_route_add_chat(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )
    
    def create_node_route_add_bot(self, user_id, name, parent_id, path, single_child):
        return self.repository.create_node_route_add_bot(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )
    
    def create_node_route_add_types_notification(self, user_id, name, parent_id, path, single_child):
        return self.repository.create_node_route_add_types_notification(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )
    
    def create_node_route_add_feature(self, user_id, name, parent_id, path, single_child):
        return self.repository.create_node_route_add_feature(
            user_id=user_id,
            name=name,
            parent_id=parent_id,
            path=path,
            single_child=single_child
        )
        
    def delete_node(self, node_id):
        return self.repository.delete_node(node_id)